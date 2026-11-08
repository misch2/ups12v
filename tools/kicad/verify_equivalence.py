"""Read-only comparison of two KiCad-exported S-expression netlists.

Ignores export date, source path, net codes and serialization order. Compares
every exported component property (including UUID/units), library definition,
net name and node property. Does not modify KiCad files.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re


TOKEN = re.compile(r'\s+|[()]|"(?:\\.|[^"\\])*"|[^()\s]+')


def parse(path):
    stack = []
    root = None
    for match in TOKEN.finditer(Path(path).read_text(encoding="utf-8-sig")):
        token = match.group()
        if token.isspace():
            continue
        if token == "(":
            item = []
            if stack:
                stack[-1].append(item)
            elif root is not None:
                raise ValueError("Multiple roots")
            else:
                root = item
            stack.append(item)
        elif token == ")":
            if not stack:
                raise ValueError("Unbalanced close parenthesis")
            stack.pop()
        else:
            if not stack:
                raise ValueError("Atom outside root")
            if token.startswith('"'):
                token = re.sub(r'\\(.)', lambda m: {"n": "\n", "r": "\r", "t": "\t"}.get(m[1], m[1]), token[1:-1])
            stack[-1].append(token)
    if stack or root is None or root[0] != "export":
        raise ValueError("Incomplete or unexpected exported netlist")
    return root


def children(item, tag):
    return [x for x in item[1:] if isinstance(x, list) and x and x[0] == tag]


def one(item, tag):
    found = children(item, tag)
    if len(found) != 1:
        raise ValueError(f"Expected one {tag}, found {len(found)}")
    return found[0]


def canonical(item):
    if not isinstance(item, list):
        return item
    atoms = [x for x in item[1:] if not isinstance(x, list)]
    subtrees = sorted((canonical(x) for x in item[1:] if isinstance(x, list)), key=repr)
    return (item[0], tuple(atoms), tuple(subtrees))


def indexed(items, key):
    result = {}
    for item in items:
        identity = one(item, key)[1]
        if identity in result:
            raise ValueError(f"Duplicate {key}: {identity}")
        result[identity] = item
    return result


def snapshot(path):
    root = parse(path)
    components = indexed(children(one(root, "components"), "comp"), "ref")
    nets = indexed(children(one(root, "nets"), "net"), "name")
    net_nodes = {name: tuple(sorted((canonical(n) for n in children(net, "node")), key=repr)) for name, net in nets.items()}
    pin_nets = {}
    for name, net in nets.items():
        for node in children(net, "node"):
            pin = f"{one(node, 'ref')[1]}.{one(node, 'pin')[1]}"
            if pin in pin_nets:
                raise ValueError(f"Pin appears twice: {pin}")
            pin_nets[pin] = name
    return {
        "components": {ref: canonical(c) for ref, c in components.items()},
        "nets": net_nodes,
        "pin_nets": pin_nets,
        "libraries": canonical(one(root, "libparts")),
    }


def differences(before, after):
    return {
        "removed": sorted(set(before) - set(after)),
        "added": sorted(set(after) - set(before)),
        "changed": sorted(k for k in before.keys() & after.keys() if before[k] != after[k]),
    }


def compare(before_path, after_path):
    before, after = snapshot(before_path), snapshot(after_path)
    result = {
        "before": str(Path(before_path).resolve()),
        "after": str(Path(after_path).resolve()),
        "before_sha256": hashlib.sha256(Path(before_path).read_bytes()).hexdigest(),
        "after_sha256": hashlib.sha256(Path(after_path).read_bytes()).hexdigest(),
        "counts_before": {k: len(before[k]) for k in ("components", "nets", "pin_nets")},
        "counts_after": {k: len(after[k]) for k in ("components", "nets", "pin_nets")},
        "components": differences(before["components"], after["components"]),
        "nets": differences(before["nets"], after["nets"]),
        "pin_nets": differences(before["pin_nets"], after["pin_nets"]),
        "library_definitions_equal": before["libraries"] == after["libraries"],
    }
    result["equivalent"] = result["library_definitions_equal"] and all(
        not any(result[key].values()) for key in ("components", "nets", "pin_nets")
    )
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("before")
    parser.add_argument("after")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    report = compare(args.before, args.after)
    Path(args.output).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("equivalent", "counts_before", "counts_after", "components", "nets", "pin_nets", "library_definitions_equal")}))
    raise SystemExit(0 if report["equivalent"] else 1)
