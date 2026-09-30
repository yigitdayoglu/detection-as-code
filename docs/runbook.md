# Operations Runbook

Procedures for running this detection pipeline day to day.

## Add a new detection

1. Branch from `main`: `git switch -c feature/<name>`.
2. Write the rule under `detections/sql/<source>/` with full metadata
   (`id`, `description`, `severity`, `status: experimental`, `mitre_attack`,
   `false_positives`, `query`).
3. Add the portable Sigma equivalent under `detections/sigma/`.
4. Add a test dataset under `tests/datasets/<source>/` with at least one
   positive case (should fire) and one negative case per exclusion (should not
   fire).
5. Run `python scripts/validate_rules.py` and `python scripts/test_rules.py`
   locally until both are green.
6. Commit, push, and open a pull request. Merge once CI passes and the change is
   reviewed.

New rules start at `status: experimental`. Promote to `stable` only after
observing their noise level in production for a period.

## Deploy

Deployment is automatic: merging to `main` runs `deploy.yml`, which syncs the
full rule set to production. To re-deploy the current state without a code
change, trigger it manually:

```bash
gh workflow run deploy.yml
gh run watch
```

## Roll back a bad rule

Production mirrors `main`, so a rollback is a git revert.

1. Find the merge commit to revert:
   ```bash
   git log --oneline main
   ```
2. Open a revert as a pull request:
   ```bash
   git switch -c revert/<name>
   git revert -m 1 <merge-commit-sha>
   git push -u origin revert/<name>
   gh pr create --title "Revert <name>" --body "Rolling back <reason>."
   ```
3. Merge the revert. The deployment pipeline re-syncs production to the reverted
   state.

For an urgent rollback, `git revert` plus merge is preferred over editing the
console directly, because it keeps `main` and production in sync and leaves an
audit trail.

## Cut a release

1. Update `VERSION` following SemVer (MINOR for a new detection, PATCH for a fix,
   MAJOR for a breaking pipeline/schema change).
2. Add a matching section to `CHANGELOG.md`.
3. Open a pull request with both changes and merge it. `release.yml` creates the
   git tag and GitHub release automatically.

## Rotate the deployment token

The RunReveal token lives in the `production` environment as `RUNREVEAL_TOKEN`.
If it leaks or expires, rotate it in place:

```bash
gh secret set RUNREVEAL_TOKEN --env production --body "<new-token>"
```

A token that was ever committed to git is considered burned. Rotate it rather
than trying to scrub history.
