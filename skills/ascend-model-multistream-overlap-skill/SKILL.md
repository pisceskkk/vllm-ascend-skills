---
name: ascend-model-multistream-overlap-skill
description: Design Ascend model multistream overlap from verified source mapping, resource-aware DAGs and paired validation.
---

# Ascend Model Multistream Overlap Skill

Use this skill for the domain task described above. The workflow below is a reference contract; choose execution tools available in the target environment.

## Core workflow

1. Capture representative prefill, decode and mixed-workload traces.
2. Map critical operators to source and construct a DAG with data, stream, alias, cache and lifetime edges.
3. Choose overlap candidates based on AIC/AIV/MTE/communication resource compatibility.
4. Verify correctness, actual overlap and paired performance before keeping a change.

## Detailed references

- [code-mapping.md](references/code-mapping.md)
- [evidence-contract.md](references/evidence-contract.md)
- [matrices.md](references/matrices.md)
- [validation.md](references/validation.md)
- [workflow.md](references/workflow.md)

## Reference code

The scripts in `scripts/` contain domain analysis or validation logic. Use them with inputs that match their documented contracts; runtime-specific tools remain external.
