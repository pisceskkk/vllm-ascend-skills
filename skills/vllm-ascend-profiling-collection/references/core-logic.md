# Profiler collection logic

Use the included `scripts/profile_control.py` against an accessible vLLM service URL. Profiling setup and finalization may take much longer than an ordinary inference request, so the control timeout is independent of request timeout.

```text
confirm service and expected rank count
  -> POST /start_profile
  -> run representative request wave plus one short follow-up request
  -> POST /stop_profile
  -> wait for profiler flush and run analyse()
  -> verify expected rank directories and required files
```

The request wave must meet an explicit success threshold, and the follow-up must succeed. A trace collected with no successful workload is unusable even if analysis exits successfully. Each expected rank output must contain `ASCEND_PROFILER_OUTPUT/kernel_details.csv` and `trace_view.json`; a missing rank or missing kernel details requires recollection.
