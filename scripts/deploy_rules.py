#!/usr/bin/env python3
"""Deploy detection rules to the RunReveal platform.

Reads every rule under detections/, then either prints the deployment
plan (--dry-run, the default) or syncs each rule to RunReveal (--apply).

The actual RunReveal API call is stubbed (sync_rule) because this project
ships no real credentials. The surrounding machinery — collecting desired
state, reading the token from the environment, per-rule reporting, and
exit codes — mirrors a real deployment.
"""
import argparse
import os
import sys
from pathlib import Path
import yaml


def collect_rules(root):
    """Load every SQL and Sigma rule as (relative_path, parsed dict)."""
    rules = []
    for sub in ("sql", "sigma"):
        for path in (root / "detections" / sub).rglob("*.yml"):
            with open(path) as f:
                rules.append((path.relative_to(root), yaml.safe_load(f)))
    return rules


def rule_identity(rule):
    """SQL rules use id/name; Sigma rules use id/title."""
    rid = rule.get("id", "<no-id>")
    label = rule.get("name") or rule.get("title") or "<unnamed>"
    return rid, label


def sync_rule(rid, label, token):
    """Push a single rule to RunReveal.

    STUB: replace the body with a real API call, e.g.
        requests.post(f"{api_url}/rules", json=payload,
                      headers={"Authorization": f"Bearer {token}"})
    For now it simulates a successful upsert.
    """
    return True


def main():
    parser = argparse.ArgumentParser(description="Deploy detection rules to RunReveal.")
    parser.add_argument("--apply", action="store_true",
                        help="Actually sync rules. Without this, runs a dry run.")
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent
    rules = collect_rules(root)

    if not args.apply:
        print(f"DRY RUN — {len(rules)} rule(s) would be deployed:\n")
        for path, rule in rules:
            rid, label = rule_identity(rule)
            print(f"  would deploy  {rid:<32} {label}  ({path})")
        print("\nNo changes sent. Re-run with --apply to deploy.")
        return 0

    token = os.environ.get("RUNREVEAL_TOKEN")
    if not token:
        print("ERROR: RUNREVEAL_TOKEN is not set. Cannot deploy.", file=sys.stderr)
        return 1

    print(f"Deploying {len(rules)} rule(s) to RunReveal...\n")
    failed = 0
    for path, rule in rules:
        rid, label = rule_identity(rule)
        ok = sync_rule(rid, label, token)
        print(f"  {'OK  ' if ok else 'FAIL'} {rid:<32} {label}")
        if not ok:
            failed += 1

    print(f"\n{len(rules) - failed}/{len(rules)} rule(s) deployed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
