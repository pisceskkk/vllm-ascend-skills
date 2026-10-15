"""Behavioral regressions using synthetic inputs, never model/NPU execution."""

import argparse
import copy
import csv
import json
import subprocess
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from analyze_kernels import measure_pairs, normalize
from common import load_json, resources, union_length
from compare_benchmarks import compare, load_runs
from validate_dag import analyze
from verify_code_map import check, inspect_site, snapshot


def event(start, duration, core="aiv", rank="r0"):
    return {"case_id": "case", "rank": rank, "phase": "decode", "resources": core,
            "start_us": str(start), "duration_us": str(duration), "end_us": str(Decimal(start) + Decimal(duration))}


def pair(pid, a, b):
    return {"pair_id": pid, "group_id": "step1/layer1", "a_event_id": a, "b_event_id": b,
            "relation": "intended_complementary", "evidence": "synthetic correlated call chain"}


class ToolsTest(unittest.TestCase):
    def test_decimal_normalization(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "kernel.csv"
            with source.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle)
                writer.writerow(["Name", "Start Time(us)", "Duration(us)", "Stream ID", "Accelerator Core"])
                writer.writerow(["vector", "1800000000000000.001", ".009", "1", "AI_VECTOR_CORE"])
                writer.writerow(["matrix", "1800000000000000.003", ".011", "2", "AI_CORE"])
            args = argparse.Namespace(input=source, out=Path(tmp)/"norm", case_id="case", rank="r0", phase="decode")
            normalize(args)
            result = load_json(args.out/"summary.json")
            self.assertEqual(result["span_us"], "0.013")
            with (args.out/"events.csv").open(newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(rows[1]["relative_start_us"], "0.002")
            self.assertEqual(result["summed_task_duration_us"], "0.020")

    def test_overlap_union_and_shared_resource_flag(self):
        events = {"a": event("0", "10"), "b": event("0", "7", "aic"), "c": event("5", "5", "aic|aiv")}
        rows, result = measure_pairs(events, [pair("1", "a", "b"), pair("2", "a", "c")])
        self.assertEqual(result["intended_complementary"]["union_overlap_us"], "10")
        self.assertEqual(result["intended_complementary"]["target_coverage"], 1)
        self.assertEqual(rows[1]["shared_resources"], "aiv")
        self.assertEqual(resources("MIX_AIC"), {"aic", "aiv"})
        self.assertEqual(resources("unrecognized"), {"unknown"})
        self.assertEqual(resources("MIX_UNRECOGNIZED"), {"unknown"})

    def test_wrong_rank_pair_rejected(self):
        with self.assertRaises(ValueError):
            measure_pairs({"a": event("0", "1"), "b": event("0", "1", rank="r1")}, [pair("1", "a", "b")])

    def test_zero_duration_coverage(self):
        rows, _ = measure_pairs({"a": event("0", "0"), "b": event("0", "2")}, [pair("1", "a", "b")])
        self.assertIsNone(rows[0]["coverage_a"])

    def test_dag_lower_bound_and_cycle(self):
        dag = load_json(ROOT/"assets/dag-example.json")
        mapping = load_json(ROOT/"assets/code-map-example.json")
        result, mermaid = analyze(dag, mapping)
        self.assertEqual(result["precedence_lower_bound_us"], "47")
        self.assertEqual(result["critical_path"], ["convert", "project", "consume"])
        self.assertIn("flowchart LR", mermaid)
        dag["edges"].append({"from": "consume", "to": "convert", "kind": "event", "evidence": ["synthetic cycle"]})
        with self.assertRaisesRegex(ValueError, "cycle"):
            analyze(dag, mapping)

    def test_unverified_mapping_rejected(self):
        mapping = load_json(ROOT/"assets/code-map-example.json")
        mapping["bindings"][0]["status"] = "hypothesis"
        with self.assertRaisesRegex(ValueError, "Unverified"):
            analyze(load_json(ROOT/"assets/dag-example.json"), mapping)

    def test_source_snapshot_and_drift(self):
        plan = load_json(ROOT/"assets/code-map-example.json")
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp)/"model.py"
            src.write_bytes((ROOT/"assets/example_source/model.py").read_bytes())
            mapping = snapshot(tmp, plan)
            self.assertEqual(check(tmp, mapping), 4)
            src.write_text(src.read_text().replace("ops.project(converted)", "ops.project(x)"))
            with self.assertRaisesRegex(ValueError, "Stale"):
                check(tmp, mapping)

    def test_source_escape_and_wrong_function_rejected(self):
        site = load_json(ROOT/"assets/code-map-example.json")["sites"][0]
        with self.assertRaises(ValueError):
            inspect_site(ROOT/"assets/example_source", dict(site, path="../model.py"))
        with self.assertRaises(ValueError):
            inspect_site(ROOT/"assets/example_source", dict(site, function="Missing.forward"))

    def test_benchmark_decisions_and_configuration_drift(self):
        base = {("c", str(i)): {"value": 100, "unit": "ms", "config_fingerprint": "fixed", "code_ref": "base"} for i in range(5)}
        cand = {k: dict(v, value=80, code_ref="candidate") for k, v in base.items()}
        result = compare(base, cand, "lower", samples=100)
        self.assertEqual(result["c"]["decision"], "improved")
        cand[("c", "0")]["config_fingerprint"] = "changed"
        with self.assertRaisesRegex(ValueError, "mismatch"):
            compare(base, cand, "lower", samples=100)

    def test_profiled_benchmark_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)/"bench.csv"
            p.write_text("case_id,pair_id,metric,value,unit,profile_enabled,config_fingerprint,code_ref\nc,1,step_ms,10,ms,true,config,ref\n")
            with self.assertRaisesRegex(ValueError, "profiler disabled"):
                load_runs(p, "step_ms")

    def test_csv_templates_are_rectangular(self):
        for path in (ROOT/"assets").glob("*.csv"):
            with self.subTest(path=path.name), path.open(newline="", encoding="utf-8-sig") as handle:
                rows = list(csv.reader(handle))
                self.assertTrue(rows)
                self.assertTrue(all(len(row) == len(rows[0]) for row in rows), path.name)

    def test_cli_source_map_and_dag(self):
        with tempfile.TemporaryDirectory() as tmp:
            mapping = Path(tmp)/"mapping.json"
            commands = [
                ["verify_code_map.py", "snapshot", "--root", str(ROOT/"assets/example_source"), "--plan", str(ROOT/"assets/code-map-example.json"), "--out", str(mapping)],
                ["verify_code_map.py", "check", "--root", str(ROOT/"assets/example_source"), "--map", str(mapping)],
                ["validate_dag.py", "--input", str(ROOT/"assets/dag-example.json"), "--code-map", str(mapping), "--out", str(Path(tmp)/"dag")],
            ]
            for command in commands:
                run = subprocess.run([sys.executable, str(ROOT/"scripts"/command[0]), *command[1:]], capture_output=True, text=True)
                self.assertEqual(run.returncode, 0, run.stderr)

    def test_cli_normalize_pairs_and_benchmark(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            kernel = tmp/"kernel.csv"
            kernel.write_text("Name,Start Time(us),Duration(us),Stream ID,Accelerator Core\nvector,1000,10,1,AI_VECTOR_CORE\nmatrix,1002,20,2,AI_CORE\n")
            pairs = tmp/"pairs.csv"
            with pairs.open("w", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(pair("p", "case:r0:2", "case:r0:3")))
                writer.writeheader()
                writer.writerow(pair("p", "case:r0:2", "case:r0:3"))
            header = "case_id,pair_id,metric,value,unit,profile_enabled,config_fingerprint,code_ref\n"
            (tmp/"base.csv").write_text(header + "".join(f"case,{i},step_ms,100,ms,false,fixed,base\n" for i in range(5)))
            (tmp/"cand.csv").write_text(header + "".join(f"case,{i},step_ms,80,ms,false,fixed,candidate\n" for i in range(5)))
            commands = [
                ["analyze_kernels.py", "normalize", "--input", str(kernel), "--out", str(tmp/"norm"), "--case-id", "case", "--rank", "r0", "--phase", "decode"],
                ["analyze_kernels.py", "pairs", "--events", str(tmp/"norm/events.csv"), "--pairs", str(pairs), "--out", str(tmp/"pairs")],
                ["compare_benchmarks.py", "--baseline", str(tmp/"base.csv"), "--candidate", str(tmp/"cand.csv"), "--metric", "step_ms", "--direction", "lower", "--out", str(tmp/"perf.json"), "--samples", "100"],
            ]
            for command in commands:
                run = subprocess.run([sys.executable, str(ROOT/"scripts"/command[0]), *command[1:]], capture_output=True, text=True)
                self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(load_json(tmp/"pairs/summary.json")["relations"]["intended_complementary"]["target_coverage"], 0.8)
            self.assertEqual(load_json(tmp/"perf.json")["cases"]["case"]["decision"], "improved")

    def test_dag_cli_rejects_stale_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            source = tmp/"model.py"
            source.write_bytes((ROOT/"assets/example_source/model.py").read_bytes())
            mapping = snapshot(tmp, load_json(ROOT/"assets/code-map-example.json"))
            (tmp/"map.json").write_text(json.dumps(mapping))
            source.write_text(source.read_text().replace("ops.project(converted)", "ops.project(x)"))
            run = subprocess.run([sys.executable, str(ROOT/"scripts/validate_dag.py"), "--input", str(ROOT/"assets/dag-example.json"), "--code-map", str(tmp/"map.json"), "--out", str(tmp/"out")], capture_output=True, text=True)
            self.assertNotEqual(run.returncode, 0)
            self.assertIn("Stale", run.stderr)


if __name__ == "__main__":
    unittest.main()
