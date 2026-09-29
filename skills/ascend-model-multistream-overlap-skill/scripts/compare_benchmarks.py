"""Paired, profiler-free benchmark comparison with per-case bootstrap intervals."""

import argparse
import csv
import math
import random
import statistics
from pathlib import Path

from common import digest, write_json


def load_runs(path, metric):
    result = {}
    required = {"case_id", "pair_id", "metric", "value", "unit", "profile_enabled", "config_fingerprint", "code_ref"}
    with Path(path).open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if not required <= set(reader.fieldnames or []):
            raise ValueError("Missing benchmark fields")
        for row in reader:
            if row["metric"] != metric:
                continue
            if not all(row[k].strip() for k in required):
                raise ValueError("Empty benchmark field")
            if row["profile_enabled"].strip().lower() not in {"false", "0", "no"}:
                raise ValueError("Performance comparison requires profiler disabled")
            key = row["case_id"], row["pair_id"]
            if key in result:
                raise ValueError("Duplicate case/pair/metric")
            row["value"] = float(row["value"])
            if not math.isfinite(row["value"]) or row["value"] <= 0:
                raise ValueError("Benchmark values must be finite and positive")
            result[key] = row
    if not result:
        raise ValueError("No records for requested metric")
    return result


def percentile(values, q):
    index = (len(values) - 1) * q
    lo = math.floor(index)
    hi = math.ceil(index)
    return values[lo] + (values[hi] - values[lo]) * (index - lo)


def compare(baseline, candidate, direction, samples=5000, confidence=0.95,
            min_pairs=5, min_gain=0.0, regression_budget=0.0, seed=0):
    if baseline.keys() != candidate.keys():
        raise ValueError("Baseline/candidate case-pair sets differ")
    if samples < 100 or min_pairs < 2 or not 0 < confidence < 1 or min_gain < 0 or regression_budget < 0:
        raise ValueError("Invalid confidence, repeat count or decision thresholds")
    if direction not in {"higher", "lower"}:
        raise ValueError("Unknown metric direction")
    cases = {}
    for key, old in baseline.items():
        new = candidate[key]
        if old["unit"] != new["unit"] or old["config_fingerprint"] != new["config_fingerprint"]:
            raise ValueError(f"Configuration/unit mismatch for {key}")
        case = cases.setdefault(key[0], [])
        case.append((key[1], old, new))
    rng = random.Random(seed)
    result = {}
    for case_id, rows in sorted(cases.items()):
        if len({(a["unit"], a["config_fingerprint"]) for _, a, _ in rows}) != 1:
            raise ValueError("Within-case configuration drift; split into separate cases")
        if len({a["code_ref"] for _, a, _ in rows}) != 1 or len({b["code_ref"] for _, _, b in rows}) != 1:
            raise ValueError("Within-case code drift; split into separate comparisons")
        rows.sort(key=lambda x: x[0])
        gains = [100 * ((b["value"] / a["value"] - 1) if direction == "higher"
                        else (1 - b["value"] / a["value"])) for _, a, b in rows]
        count = len(gains)
        resampled = sorted(statistics.fmean(rng.choices(gains, k=count)) for _ in range(samples))
        low = percentile(resampled, (1 - confidence) / 2)
        high = percentile(resampled, (1 + confidence) / 2)
        if count < min_pairs:
            decision = "insufficient_repeats"
        elif high < -regression_budget:
            decision = "regressed"
        elif low > min_gain:
            decision = "improved"
        elif low >= -regression_budget:
            decision = "within_regression_budget"
        else:
            decision = "inconclusive"
        result[case_id] = {"pairs": count, "mean_paired_improvement_pct": statistics.fmean(gains),
                           "improvement_interval_pct": [low, high], "confidence": confidence,
                           "baseline_median": statistics.median(a["value"] for _, a, _ in rows),
                           "candidate_median": statistics.median(b["value"] for _, _, b in rows),
                           "unit": rows[0][1]["unit"], "decision": decision,
                           "pair_improvement_pct": dict(zip((p for p, _, _ in rows), gains))}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--metric", required=True)
    parser.add_argument("--direction", choices=["higher", "lower"], required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--samples", type=int, default=5000)
    parser.add_argument("--confidence", type=float, default=0.95)
    parser.add_argument("--min-pairs", type=int, default=5)
    parser.add_argument("--min-gain-pct", type=float, default=0)
    parser.add_argument("--regression-budget-pct", type=float, default=0)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    try:
        result = compare(load_runs(args.baseline, args.metric), load_runs(args.candidate, args.metric),
                         args.direction, args.samples, args.confidence, args.min_pairs,
                         args.min_gain_pct, args.regression_budget_pct, args.seed)
        write_json(args.out, {"metric": args.metric, "direction": args.direction,
                             "baseline_sha256": digest(args.baseline), "candidate_sha256": digest(args.candidate),
                             "bootstrap_seed": args.seed, "bootstrap_samples": args.samples,
                             "min_pairs": args.min_pairs, "min_gain_pct": args.min_gain_pct,
                             "regression_budget_pct": args.regression_budget_pct, "cases": result,
                             "limitation": "Intervals depend on representative independent measurement blocks; correctness and overlap require separate gates."})
        print(f"Compared {len(result)} cases; see {args.out}")
    except (ValueError, KeyError, OSError) as exc:
        parser.exit(2, f"error: {exc}\n")


if __name__ == "__main__":
    main()
