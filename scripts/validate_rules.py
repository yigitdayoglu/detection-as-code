#!/usr/bin/env python3
"""Validate detection rules against schema and team policy.

Static checks only — this never executes a rule, it only reads it.
Exits non-zero if any rule fails, so CI can gate on it.
"""
import sys
from pathlib import Path
import yaml

ALLOWED_SEVERITY = {"low", "medium", "high", "critical"}
ALLOWED_STATUS = {"experimental", "stable", "deprecated"}

SQL_REQUIRED = ["id", "name", "description", "severity", "status",
                "logsource", "false_positives", "query"]
SIGMA_REQUIRED = ["title", "id", "status", "description",
                  "logsource", "detection", "level", "falsepositives"]


def validate_sql_rule(rule):
    errors = []
    for field in SQL_REQUIRED:
        if field not in rule or rule[field] in (None, "", []):
            errors.append(f"missing required field: {field}")
    if rule.get("severity") not in ALLOWED_SEVERITY:
        errors.append(f"severity '{rule.get('severity')}' not allowed")
    if rule.get("status") not in ALLOWED_STATUS:
        errors.append(f"status '{rule.get('status')}' not allowed")
    return errors


def validate_sigma_rule(rule):
    errors = []
    for field in SIGMA_REQUIRED:
        if field not in rule or rule[field] in (None, "", []):
            errors.append(f"missing required field: {field}")
    if rule.get("level") not in ALLOWED_SEVERITY:
        errors.append(f"level '{rule.get('level')}' not allowed")
    if rule.get("status") not in ALLOWED_STATUS:
        errors.append(f"status '{rule.get('status')}' not allowed")
    return errors


def check(paths, validator, root):
    failed = 0
    for path in paths:
        rel = path.relative_to(root)
        try:
            with open(path) as f:
                rule = yaml.safe_load(f)
            errors = validator(rule)
        except yaml.YAMLError as e:
            errors = [f"invalid YAML: {e}"]
        if errors:
            failed += 1
            print(f"FAIL {rel}")
            for e in errors:
                print(f"     - {e}")
        else:
            print(f"PASS {rel}")
    return len(paths), failed


def main():
    root = Path(__file__).resolve().parent.parent
    sql = list((root / "detections" / "sql").rglob("*.yml"))
    sigma = list((root / "detections" / "sigma").rglob("*.yml"))

    n1, f1 = check(sql, validate_sql_rule, root)
    n2, f2 = check(sigma, validate_sigma_rule, root)

    total, failed = n1 + n2, f1 + f2
    print(f"\n{total - failed}/{total} rules passed validation")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
