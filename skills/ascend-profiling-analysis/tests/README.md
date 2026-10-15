# ascend-profiling-analysis tests

Portable unit and integration tests using synthetic inputs. They run locally
without Ascend NPU hardware, GPU inference or remote SSH.

The suite covers segment manifests and validation, HTML diagnosis output,
attention and MoE families, kernel signatures and semantic conventions.
Install `pytest` and `PyYAML` to run the complete suite; YAML-dependent tests
may be skipped when `PyYAML` is unavailable.

Run from the repository root:

```bash
python3 -m pytest skills/ascend-profiling-analysis/tests -q
```

To run one test module:

```bash
python3 -m pytest skills/ascend-profiling-analysis/tests/test_manifest_schema.py -q
```
