# One-state measurement logic

Build a resolved configuration from explicit user values, with optional model/nightly defaults filling only missing fields. Hold the service constant across warmup and measured rounds. For each round preserve the raw output, normalized metrics, workload parameters and success status. Aggregate only measured rounds with count, per-metric values, mean and sample standard deviation. Stop the owned service on both success and failure, and retain completed rounds if a later round fails.

`aisbench_auto_tools` is an external performance runner. Its output must be checked for missing or sentinel metrics before a measurement is accepted. `vllm bench serve` is an alternative external runner when selected explicitly. This Skill measures one code state; code-state comparison belongs to performance regression.
