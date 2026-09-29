# HBM attribution logic

The included `scripts/mem_analyze.py` parses vLLM logs, NPU HBM samples and msprof component CSVs. `weight_inspector.py` estimates weight bytes from model files. The analysis separates fixed process overhead, weights, KV cache, HCCL, activations and runtime allocations, then cross-checks them against observed device use.

Use measurements from one aligned serving run. Record the source for each component and report residual memory explicitly. Weight file size, loaded tensor bytes and runtime allocated HBM are distinct quantities; do not sum them without checking scope and overlap. `msprof` collection and `torch_npu` execution require an external Ascend runtime.
