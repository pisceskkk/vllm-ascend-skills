---
name: vllm-ascend-serving
description: Plan and review one colocated vLLM Ascend service lifecycle, including source pairing, device selection, launch, health, and cleanup.
---

# Vllm Ascend Serving

Use this skill for the domain task described above. The workflow below is a reference contract; choose execution tools available in the target environment.

## Core workflow

1. Confirm the vLLM and vllm-ascend source pair and record the model, topology, devices, environment and launch arguments.
2. Check device availability and model path, then choose a free service port.
3. Launch with individually quoted arguments; retain PID, logs and the resolved configuration.
4. Require healthy /health and nonempty /v1/models responses before reporting readiness.
5. On stop or failed startup, identify the owned process and record cleanup evidence.

Read [core logic](references/core-logic.md) when planning or reviewing the implementation.
