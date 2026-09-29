---
name: vllm-ascend-serving
description: Plan and review one colocated vLLM Ascend service lifecycle, including source pairing, device selection, launch, health, and cleanup.
---

# Vllm Ascend Serving

Use this skill for the domain task described above. The workflow below is a reference contract; choose execution tools available in the target environment.

## Core workflow

1. Resolve the vLLM version against the checked-out vllm-ascend revision. Prefer the verified main2main commit; use the matched release tag when a release version is requested.
2. If the user has no service script or launch command, derive one from the matching model and feature documentation and a relevant nightly case at that vllm-ascend revision.
3. If no parallel strategy is specified, choose a supported topology from the workload, model memory needs, server count and available NPU count. Record the per-node device and rank mapping.
4. Check device availability and model path, then choose a free service port. Record the resolved commit, model, topology, environment and launch arguments.
5. Launch with individually quoted arguments; retain PID, service logs and the resolved configuration. For operator failures, preserve relevant container plog from `~/ascend/log/debug/` before teardown.
6. Require healthy /health and nonempty /v1/models responses before reporting readiness.
7. On stop or failed startup, stop the owned process tree, ensure exited children are reaped, and record cleanup evidence. Check NPU occupancy when release is uncertain.

Read [core logic](references/core-logic.md) when planning or reviewing the implementation.
Read [launch configuration](references/launch-configuration.md) when deriving a command or topology.
