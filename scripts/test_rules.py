#!/usr/bin/env python3
"""Run detection rules against their test datasets.

For each dataset, find the SQL rule it targets (matched by rule id),
evaluate the rule's logic against every synthetic event, and compare
the result to the expected outcome.

This SIMULATES the detection logic in Python — it does not run a real
SQL engine. It supports the subset of SQL our rules use: a WHERE clause
of AND-joined equality (=) and inequality (!=) predicates.
"""
import json
import re
import sys
from pathlib import Path
import yaml

PREDICATE = re.compile(r"([\w.]+)\s*(=|!=)\s*'([^']*)'")


def get_field(event, dotted):
    """Look up a dotted path like 'userIdentity.type' in a nested dict."""
    value = event
    for part in dotted.split("."):
        if not isinstance(value, dict) or part not in value:
            return None
        value = value[part]
    return value


def parse_where(query):
    """Extract (field, operator, value) predicates from a WHERE clause."""
    idx = query.lower().find("where")
    if idx == -1:
        raise ValueError("query has no WHERE clause")
    return PREDICATE.findall(query[idx + len("where"):])


def event_matches(event, predicates):
    """True only if the event satisfies ALL predicates (AND semantics)."""
    for field, op, expected in predicates:
        actual = get_field(event, field)
        if op == "=" and actual != expected:
            return False
        if op == "!=" and actual == expected:
            return False
    return True


def load_rules_by_id(root):
    rules = {}
    for path in (root / "detections" / "sql").rglob("*.yml"):
        with open(path) as f:
            rule = yaml.safe_load(f)
        rules[rule["id"]] = rule
    return rules


def main():
    root = Path(__file__).resolve().parent.parent
    rules = load_rules_by_id(root)
    datasets = list((root / "tests" / "datasets").rglob("*.json"))

    total, failed = 0, 0
    for ds_path in datasets:
        with open(ds_path) as f:
            dataset = json.load(f)
        rule_id = dataset["rule_id"]

        if rule_id not in rules:
            print(f"ERROR {ds_path.name}: no rule with id '{rule_id}'")
            failed += 1
            continue

        predicates = parse_where(rules[rule_id]["query"])
        for case in dataset["cases"]:
            total += 1
            got = event_matches(case["event"], predicates)
            want = case["expect_match"]
            ok = "PASS" if got == want else "FAIL"
            if got != want:
                failed += 1
            print(f"{ok} [{rule_id}] {case['name']}: want={want} got={got}")

    print(f"\n{total - failed}/{total} test cases passed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
