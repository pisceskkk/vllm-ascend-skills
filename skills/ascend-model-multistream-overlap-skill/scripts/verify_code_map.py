"""Snapshot/check source anchors without importing or executing model code."""

import argparse
import ast
import hashlib
from pathlib import Path

from common import digest, load_json, write_json


def qualified_scopes(tree):
    result = {}

    def walk(node, prefix):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                name = ".".join(prefix + [child.name])
                if name in result:
                    raise ValueError(f"Ambiguous conditional/redefined scope: {name}")
                result[name] = child
                walk(child, prefix + [child.name])
            else:
                walk(child, prefix)
    walk(tree, [])
    return result


def inspect_site(root, site):
    root = Path(root).resolve()
    path = (root / site["path"]).resolve()
    if Path(site["path"]).is_absolute() or not path.is_relative_to(root):
        raise ValueError("Source path must resolve inside the source root")
    raw = path.read_bytes()
    # tokenize.open honors the Python source encoding declaration.
    import tokenize
    with tokenize.open(path) as handle:
        text = handle.read()
    tree = ast.parse(text, filename=str(path))
    scope = qualified_scopes(tree).get(site["function"])
    if scope is None or not isinstance(scope, (ast.FunctionDef, ast.AsyncFunctionDef)):
        raise ValueError(f"Function not found: {site['function']}")
    start, end = site["start_line"], site["end_line"]
    if type(start) is not int or type(end) is not int or not scope.lineno <= start <= end <= scope.end_lineno:
        raise ValueError(f"Anchor outside function: {site['id']}")
    fragment = "".join(text.splitlines(keepends=True)[start-1:end])
    if not fragment.strip():
        raise ValueError("Empty source anchor")
    return {"file_sha256": hashlib.sha256(raw).hexdigest(),
            "fragment_sha256": hashlib.sha256(fragment.encode("utf-8")).hexdigest(),
            "source_excerpt": fragment, "function_start": scope.lineno, "function_end": scope.end_lineno}


def validate_structure(mapping):
    if mapping.get("schema_version") != 1:
        raise ValueError("Expected code-map schema_version=1")
    sites = {}
    for site in mapping.get("sites", []):
        sid = site.get("id")
        if not sid or sid in sites:
            raise ValueError("Missing/duplicate code site id")
        if not site.get("call_chain") or not isinstance(site["call_chain"], list):
            raise ValueError("Each site needs its expanded static call chain")
        contract = site.get("tensor_contract", {})
        if not {"inputs", "outputs", "reads", "writes", "aliases", "side_effects"} <= contract.keys():
            raise ValueError("Incomplete tensor contract")
        sites[sid] = site
    if not sites:
        raise ValueError("No code sites")
    for binding in mapping.get("bindings", []):
        if not binding.get("operator_id") or not binding.get("code_sites"):
            raise ValueError("Binding needs operator_id and code_sites")
        if set(binding["code_sites"]) - sites.keys():
            raise ValueError("Binding refers to unknown code site")
        if binding.get("status") not in {"verified", "hypothesis"}:
            raise ValueError("Binding status must be verified or hypothesis")
        if binding["status"] == "verified" and (not binding.get("static_evidence") or not binding.get("runtime_evidence")):
            raise ValueError("Verified mapping requires static and runtime evidence")
    return sites


def snapshot(root, plan):
    validate_structure(plan)
    result = dict(plan, source_root=str(Path(root).resolve()))
    result["sites"] = [dict(site, **inspect_site(root, site)) for site in plan["sites"]]
    return result


def check(root, mapping):
    sites = validate_structure(mapping)
    stale = []
    for sid, site in sites.items():
        current = inspect_site(root, site)
        if any(site.get(k) != current[k] for k in ("file_sha256", "fragment_sha256", "function_start", "function_end")):
            stale.append(sid)
    if stale:
        raise ValueError(f"Stale source anchors; recheck mapping: {', '.join(stale)}")
    return len(sites)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("snapshot")
    p.add_argument("--root", required=True)
    p.add_argument("--plan", required=True)
    p.add_argument("--out", required=True)
    p = sub.add_parser("check")
    p.add_argument("--root", required=True)
    p.add_argument("--map", required=True)
    args = parser.parse_args()
    try:
        if args.command == "snapshot":
            result = snapshot(args.root, load_json(args.plan))
            result["plan_sha256"] = digest(args.plan)
            write_json(args.out, result)
            print(f"Saved {len(result['sites'])} anchors; runtime mapping status is caller supplied.")
        else:
            count = check(args.root, load_json(args.map))
            print(f"PASS: {count} source anchors match; this does not prove runtime correspondence.")
    except (ValueError, KeyError, OSError, SyntaxError) as exc:
        parser.exit(2, f"error: {exc}\n")


if __name__ == "__main__":
    main()
