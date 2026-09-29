---
name: vllm-ascend-distributed-debug
description: Diagnose Ascend multi-rank startup, collective, endpoint and hang failures using explicit topology and per-rank evidence.
---

# Vllm Ascend Distributed Debug

Use this skill for the domain task described above. The workflow below is a reference contract; choose execution tools available in the target environment.

## Core workflow

1. Record ranks, devices, groups, endpoints and the exact failing operation or progress marker.
2. Align per-rank events to find the first missing or delayed participant.
3. Reduce one parallel dimension at a time while preserving the failure signature.
4. Verify the fix in the smallest reproducer and original topology.

## Detailed references

- [acceptance.md](references/acceptance.md)
- [behavior.md](references/behavior.md)
