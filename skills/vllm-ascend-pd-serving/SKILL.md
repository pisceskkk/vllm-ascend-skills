---
name: vllm-ascend-pd-serving
description: Plan and review prefill/decode vLLM Ascend serving with explicit roles, connectors, ordering and KV transfer evidence.
---

# Vllm Ascend Pd Serving

Use this skill for the domain task described above. The workflow below is a reference contract; choose execution tools available in the target environment.

## Core workflow

1. Define prefill and decode roles, parallel topology, model identity and connector settings.
2. Verify all roles use an identical source snapshot; start in declared order and check each endpoint.
3. Check proxy health and send a request that exercises KV transfer.
4. Keep per-role logs and rollback instructions; stop only the deployment being reviewed.

## Detailed references

- [acceptance.md](references/acceptance.md)
- [behavior.md](references/behavior.md)
