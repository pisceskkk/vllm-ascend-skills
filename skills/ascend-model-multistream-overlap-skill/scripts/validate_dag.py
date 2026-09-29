"""Validate an evidence-bound DAG and compute a precedence-only lower bound."""

import argparse
from collections import deque
from decimal import Decimal

from common import digest, load_json, new_dir, number, write_json
from verify_code_map import check, validate_structure


KINDS = {"data", "stream", "event", "alias", "cache", "collective", "lifetime"}
RESOURCES = {"aic", "aiv", "cpu", "communication", "memory", "unknown"}


def analyze(dag, mapping):
    if bool(dag.get("context", {}).get("synthetic")) != bool(mapping.get("context", {}).get("synthetic")):
        raise ValueError("Synthetic and real evidence must not be mixed")
    sites = validate_structure(mapping)
    nodes, durations, successors, indegree = {}, {}, {}, {}
    for node in dag.get("nodes", []):
        nid = node.get("id")
        if not nid or nid in nodes:
            raise ValueError("Missing/duplicate DAG node id")
        duration = number(node["duration_us"])
        if duration < 0 or not node.get("label") or not node.get("evidence"):
            raise ValueError("Node needs nonnegative duration, label and evidence")
        if not node.get("resources") or set(node["resources"]) - RESOURCES:
            raise ValueError("Node has missing/unknown resource labels")
        code_sites = set(node.get("code_sites", []))
        if not code_sites or code_sites - sites.keys():
            raise ValueError("Every node needs valid code_sites")
        matched = set()
        for binding in mapping.get("bindings", []):
            if binding["operator_id"] == nid and binding["status"] == "verified":
                matched.update(binding["code_sites"])
        if not code_sites <= matched:
            raise ValueError(f"Unverified runtime/source correspondence for {nid}")
        nodes[nid], durations[nid] = node, duration
        successors[nid], indegree[nid] = [], 0
    if not nodes:
        raise ValueError("Empty DAG")
    links = set()
    seen_edges = set()
    for edge in dag.get("edges", []):
        a, b, kind = edge["from"], edge["to"], edge["kind"]
        if a not in nodes or b not in nodes or a == b or kind not in KINDS or not edge.get("evidence"):
            raise ValueError("Invalid/unsubstantiated DAG edge")
        key = (a, b, kind)
        if key in seen_edges:
            raise ValueError("Duplicate DAG edge")
        seen_edges.add(key)
        if (a, b) not in links:
            successors[a].append(b)
            indegree[b] += 1
            links.add((a, b))
    queue = deque(n for n in nodes if not indegree[n])
    starts = {n: Decimal(0) for n in nodes}
    parent, order = {}, []
    while queue:
        n = queue.popleft()
        order.append(n)
        for child in successors[n]:
            finish = starts[n] + durations[n]
            if finish > starts[child]:
                starts[child], parent[child] = finish, n
            indegree[child] -= 1
            if not indegree[child]:
                queue.append(child)
    if len(order) != len(nodes):
        raise ValueError("Dependency cycle")
    finish = {n: starts[n] + durations[n] for n in nodes}
    tail = max(nodes, key=lambda n: finish[n])
    critical = [tail]
    while critical[-1] in parent:
        critical.append(parent[critical[-1]])
    result = {"context": dag.get("context"), "topological_order": order,
              "precedence_lower_bound_us": str(finish[tail]),
              "critical_path": list(reversed(critical)),
              "earliest_start_us": {n: str(v) for n, v in starts.items()},
              "earliest_finish_us": {n: str(v) for n, v in finish.items()},
              "limitation": "Not a hardware simulation: excludes contention, launch costs, bandwidth and changed kernel durations."}
    aliases = {n: f"n{i}" for i, n in enumerate(nodes)}
    lines = ["flowchart LR"]
    for n, node in nodes.items():
        label = f"{n}: {node['label']} ({durations[n]} us; {','.join(node['resources'])})"
        label = label.replace("&", "&amp;").replace('"', "&quot;").replace("\n", " ")
        lines.append(f'  {aliases[n]}["{label}"]')
    for edge in dag.get("edges", []):
        lines.append(f"  {aliases[edge['from']]} -->|{edge['kind']}| {aliases[edge['to']]}")
    return result, "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--code-map", required=True)
    parser.add_argument("--source-root", help="Override the source root saved in the code-map snapshot")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    try:
        mapping = load_json(args.code_map)
        root = args.source_root or mapping.get("source_root")
        if not root:
            raise ValueError("Snapshot source anchors before validating the DAG")
        check(root, mapping)
        result, mermaid = analyze(load_json(args.input), mapping)
        result.update(dag_sha256=digest(args.input), code_map_sha256=digest(args.code_map))
        out = new_dir(args.out)
        write_json(out / "analysis.json", result)
        with (out / "dag.mmd").open("x", encoding="utf-8") as handle:
            handle.write(mermaid)
        print(f"Validated DAG; precedence lower bound: {result['precedence_lower_bound_us']} us")
    except (ValueError, KeyError, OSError) as exc:
        parser.exit(2, f"error: {exc}\n")


if __name__ == "__main__":
    main()
