# Validation rules

Use the diff and affected execution paths to select a minimum meaningful check set. Unknown paths need manual review.

| Change area | Required evidence |
| --- | --- |
| Attention backend | Correctness on the affected backend and eager mode; graph mode when used |
| Build or dependencies | Package build and import smoke |
| Custom operator or kernel | Dtype, shape and layout matrix plus model smoke |
| Graph execution | Eager versus graph comparison |
| KV cache or connector | Feature matrix or transfer smoke, including affected topology |
| Model adapter or runner | Model smoke and relevant override path |
| Parallel metadata or worker | Rank consistency and multi-rank smoke |
| Quantization | Dtype and model smoke |
| Scheduler | Online request cases for affected scheduling behavior |
| Tests | Targeted test suite |

These rules are distilled from the source workspace's formal validation rules. The target project may have more specific or newer rules; record the rule source used in each plan.
