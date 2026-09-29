# Service lifecycle logic

The service controller in a target environment should implement the following state machine:

```text
resolve source pair and target
  -> derive missing launch configuration and topology from current project evidence
  -> validate model path, topology, devices and available port
  -> launch with individually quoted arguments
  -> persist PID and resolved configuration
  -> poll /health and /v1/models
  -> ready or failed with logs and cleanup evidence
```

## Source pairing

Read compatibility markers from the **checked-out vllm-ascend revision** before selecting vLLM:

- `vllm-ascend/.github/vllm-main-verified.commit` identifies the verified vLLM main commit. Select this main2main pair by default.
- `vllm-ascend/.github/vllm-release-tag.commit` identifies the matched vLLM release tag. When a release version is requested, check that it matches the recorded tag, resolve the tag to an exact vLLM commit, and record both values.

For another explicitly requested vLLM version, require an explicit compatible commit or validation evidence. Record the vllm-ascend revision, selected mode, marker value and resolved vLLM commit; fail the pairing check when a marker is missing or the checked-out vLLM revision differs. The release marker is a tag, so it must be resolved before comparing commits.

## Evidence retained

Preserve the exact launch command, PID or process-group identity, startup and service logs, and resolved configuration, while omitting secrets from durable reports. For an operator error, retain the relevant plog from the container's `~/ascend/log/debug/` when available. Record its container path, time window and rank/device context so it can be correlated with the service error. Capture this evidence before deleting a failed runtime.

A relaunch merges explicitly supplied settings with the previous configuration and recalculates runtime-only fields such as PID and port.

## Stop and failure cleanup

Stop only the recorded service process tree. Request graceful shutdown first, then escalate for owned processes that remain alive; wait for child exit and parent reaping. A defunct process cannot be killed directly: identify its parent and allow it to reap the child, or stop the owned parent when appropriate. Check the process tree again before reporting cleanup complete. If device release is uncertain, inspect `npu-smi` occupancy and record any remaining process or HBM use rather than assuming the NPU is free.
