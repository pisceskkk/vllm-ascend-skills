#!/usr/bin/env python3
"""Control an already running vLLM torch-profiler window over HTTP."""

from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.request


def post_profile_action(base_url: str, action: str, timeout: int = 600) -> dict:
    if action not in {"start_profile", "stop_profile"}:
        raise ValueError(f"unsupported profiler action: {action}")
    if timeout <= 0:
        raise ValueError("timeout must be positive")
    url = f"{base_url.rstrip('/')}/{action}"
    request = urllib.request.Request(url, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8", errors="replace")
            return {"ok": True, "status": response.status, "body": body}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return {"ok": False, "status": exc.code, "body": body}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--action", required=True, choices=("start_profile", "stop_profile"))
    parser.add_argument("--timeout", type=int, default=600)
    args = parser.parse_args()
    result = post_profile_action(args.base_url, args.action, args.timeout)
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
