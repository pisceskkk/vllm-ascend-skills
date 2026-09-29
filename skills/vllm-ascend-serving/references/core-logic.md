# Service lifecycle logic

The service controller in a target environment should implement the following state machine:

```text
resolve source pair and target
  -> validate model path, topology, devices and available port
  -> launch with individually quoted arguments
  -> persist PID and resolved configuration
  -> poll /health and /v1/models
  -> ready or failed with logs and cleanup evidence
```

Check the permitted vLLM commit against the verified pin carried by the checked-out vllm-ascend source before launch. Preserve the exact command and environment, but omit secrets from durable reports. A relaunch merges explicitly supplied settings with the previous configuration and recalculates runtime-only fields such as PID and port. Stop must act on the process identified by the selected service state, then verify it exited.
