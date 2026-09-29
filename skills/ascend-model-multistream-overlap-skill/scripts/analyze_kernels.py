"""Normalize Ascend kernel CSV and measure explicitly evidenced event pairs."""

import argparse
import csv
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

from common import digest, fraction, new_dir, number, resources, union_length, write_json


FIELDS = ["event_id", "case_id", "rank", "phase", "source_row", "name", "stream",
          "task_type", "resources", "shape", "dtype", "model_id", "start_us",
          "duration_us", "end_us", "relative_start_us"]


def kernel_rows(path):
    required = {"Name", "Start Time(us)", "Duration(us)", "Stream ID"}
    with Path(path).open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if not required.issubset(reader.fieldnames or []):
            raise ValueError(f"Missing CSV columns: {sorted(required - set(reader.fieldnames or []))}")
        for row_id, row in enumerate(reader, 2):
            start, duration = number(row["Start Time(us)"]), number(row["Duration(us)"])
            if duration < 0:
                raise ValueError(f"Negative duration at CSV record {row_id}")
            yield row_id, row, start, duration


def normalize(args):
    source_hash = digest(args.input)
    origin = None
    last_end = None
    for _, _, start, duration in kernel_rows(args.input):
        origin = start if origin is None else min(origin, start)
        last_end = start + duration if last_end is None else max(last_end, start + duration)
    if origin is None:
        raise ValueError("No kernel records")
    out = new_dir(args.out)
    intervals = defaultdict(list)
    operators = {}
    total, count = Decimal(0), 0
    with (out / "events.csv").open("x", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        for row_id, row, start, duration in kernel_rows(args.input):
            task = row.get("Accelerator Core") or row.get("Task Type") or "unknown"
            core = resources(task)
            shape, dtype = row.get("Input Shapes", ""), row.get("Input Data Types", "")
            writer.writerow(dict(zip(FIELDS, [
                f"{args.case_id}:{args.rank}:{row_id}", args.case_id, args.rank, args.phase,
                row_id, row["Name"], row["Stream ID"], task, "|".join(sorted(core)),
                shape, dtype, row.get("Model ID", ""), str(start), str(duration),
                str(start + duration), str(start - origin),
            ])))
            for resource in core:
                intervals[resource].append((start, start + duration))
            key = (row["Name"], task, shape, dtype)
            entry = operators.setdefault(key, {"calls": 0, "duration": Decimal(0)})
            entry["calls"] += 1
            entry["duration"] += duration
            total += duration
            count += 1
    if digest(args.input) != source_hash:
        raise ValueError("Source changed during normalization; discard this partial output")
    ranked = []
    for (name, task, shape, dtype), entry in sorted(operators.items(), key=lambda x: x[1]["duration"], reverse=True):
        ranked.append({"name": name, "task_type": task, "shape": shape, "dtype": dtype,
                       "calls": entry["calls"], "duration_us": str(entry["duration"]),
                       "task_duration_share": fraction(entry["duration"], total)})
    result = {"source": str(Path(args.input).resolve()), "source_sha256": source_hash,
              "case_id": args.case_id, "rank": args.rank, "phase": args.phase,
              "origin_us": str(origin), "span_us": str(last_end - origin), "events": count,
              "summed_task_duration_us": str(total),
              "resource_time_union_us": {k: str(union_length(v)) for k, v in intervals.items()},
              "operators": ranked,
              "limitations": ["Time coverage is not core utilization or critical-path contribution.",
                              "Phase/rank are caller supplied; verify them against runtime evidence."]}
    write_json(out / "summary.json", result)
    print(f"Normalized {count} events into {out}")


def measure_pairs(events, pairs):
    rows, groups, ids = [], {}, set()
    target_groups = {}
    for pair in pairs:
        if not all(pair.get(k, "").strip() for k in ("pair_id", "group_id", "a_event_id", "b_event_id", "relation", "evidence")):
            raise ValueError("Pair requires IDs, relation, group and semantic evidence")
        if pair["pair_id"] in ids:
            raise ValueError("Duplicate pair_id")
        ids.add(pair["pair_id"])
        if pair["relation"] not in {"intended_complementary", "suspected_contention"}:
            raise ValueError("Unknown pair relation")
        aid, bid = pair["a_event_id"], pair["b_event_id"]
        if aid == bid or aid not in events or bid not in events:
            raise ValueError("Invalid/missing event IDs")
        a, b = events[aid], events[bid]
        if any(a[k] != b[k] for k in ("case_id", "rank", "phase")):
            raise ValueError("Cross-case/rank/phase pairing requires separate aligned analysis")
        start = max(number(a["start_us"]), number(b["start_us"]))
        end = min(number(a["end_us"]), number(b["end_us"]))
        overlap = max(Decimal(0), end - start)
        da, db = number(a["duration_us"]), number(b["duration_us"])
        shared = set(a["resources"].split("|")) & set(b["resources"].split("|"))
        unknown = "unknown" in set(a["resources"].split("|")) | set(b["resources"].split("|"))
        row = dict(pair, overlap_us=str(overlap), coverage_a=fraction(overlap, da),
                   coverage_b=fraction(overlap, db),
                   launch_skew_us=str(number(b["start_us"]) - number(a["start_us"])),
                   shared_resources="|".join(sorted(shared - {"unknown"})), resource_unknown=unknown)
        rows.append(row)
        target = (pair["relation"], aid)
        if target in target_groups and target_groups[target] != pair["group_id"]:
            raise ValueError("One target event cannot belong to two semantic groups")
        target_groups[target] = pair["group_id"]
        group = groups.setdefault(target, {"duration": da, "intervals": []})
        if overlap:
            group["intervals"].append((start, end))
    totals = {}
    for (relation, _), value in groups.items():
        total = totals.setdefault(relation, {"targets": 0, "duration": Decimal(0), "overlap": Decimal(0)})
        total["targets"] += 1
        total["duration"] += value["duration"]
        total["overlap"] += union_length(value["intervals"])
    summary = {k: {"target_count": v["targets"], "target_duration_us": str(v["duration"]),
                   "union_overlap_us": str(v["overlap"]), "target_coverage": fraction(v["overlap"], v["duration"])}
               for k, v in totals.items()}
    return rows, summary


def pair_command(args):
    with Path(args.pairs).open(newline="", encoding="utf-8-sig") as handle:
        pairs = list(csv.DictReader(handle))
    if not pairs:
        raise ValueError("No pair evidence")
    wanted = {p[k] for p in pairs for k in ("a_event_id", "b_event_id")}
    events = {}
    with Path(args.events).open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            if row["event_id"] in wanted:
                if row["event_id"] in events:
                    raise ValueError("Duplicate event_id")
                start, end, dur = (number(row[k]) for k in ("start_us", "end_us", "duration_us"))
                if dur < 0 or end - start != dur:
                    raise ValueError("Invalid normalized event interval")
                events[row["event_id"]] = row
    rows, summary = measure_pairs(events, pairs)
    out = new_dir(args.out)
    with (out / "pairs.csv").open("x", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    write_json(out / "summary.json", {"relations": summary, "events_sha256": digest(args.events),
                                      "pairs_sha256": digest(args.pairs),
                                      "limitation": "Resource sharing is a risk flag, not proof of contention or speedup."})
    print(f"Measured {len(rows)} explicit pairs into {out}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("normalize")
    p.add_argument("--input", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--case-id", required=True)
    p.add_argument("--rank", required=True)
    p.add_argument("--phase", choices=["prefill", "decode", "mixed", "unknown"], required=True)
    p.set_defaults(run=normalize)
    p = sub.add_parser("pairs")
    p.add_argument("--events", required=True)
    p.add_argument("--pairs", required=True)
    p.add_argument("--out", required=True)
    p.set_defaults(run=pair_command)
    args = parser.parse_args()
    try:
        args.run(args)
    except (ValueError, KeyError, OSError) as exc:
        parser.exit(2, f"error: {exc}\n")


if __name__ == "__main__":
    main()
