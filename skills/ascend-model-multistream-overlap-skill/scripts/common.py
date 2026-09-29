"""Standard-library helpers; these tools never execute model code."""

import hashlib
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path


def number(value):
    try:
        result = Decimal(str(value).strip())
    except InvalidOperation as exc:
        raise ValueError(f"Invalid number: {value!r}") from exc
    if not result.is_finite():
        raise ValueError(f"Non-finite number: {value!r}")
    return result


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def write_json(path, value):
    with Path(path).open("x", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def new_dir(path):
    result = Path(path)
    result.mkdir(parents=True, exist_ok=False)
    return result


def union_length(intervals):
    total = Decimal(0)
    end = None
    for start, stop in sorted(intervals):
        if stop < start:
            raise ValueError("Reversed interval")
        if end is None or start >= end:
            total += stop - start
        elif stop > end:
            total += stop - end
        end = stop if end is None else max(end, stop)
    return total


def resources(task_type):
    value = str(task_type).strip().upper()
    if value in {"MIX_AIC", "MIX_AIV"}:
        return {"aic", "aiv"}
    return {
        "AI_CORE": {"aic"}, "AI_VECTOR_CORE": {"aiv"},
        "AI_CPU": {"cpu"}, "AICPU": {"cpu"},
        "COMMUNICATION": {"communication"}, "HCCL": {"communication"},
    }.get(value, {"unknown"})


def fraction(part, whole):
    return float(part / whole) if whole else None
