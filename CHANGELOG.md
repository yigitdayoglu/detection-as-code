# Changelog

All notable changes to this detection rule set are recorded here. The format
follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the
project uses [Semantic Versioning](https://semver.org/): `MAJOR.MINOR.PATCH`,
where a new detection is a MINOR bump, a fix to an existing detection is a
PATCH, and a breaking change to the pipeline or rule schema is a MAJOR bump.

## [0.1.0] - 2026-07-21

### Added
- AWS Console Login Without MFA detection (SQL and Sigma), excluding federated
  and SSO logins whose MFA is enforced at the identity provider.
- AWS Root Account Usage detection (SQL), flagging any activity by the account
  root user.
- Synthetic CloudTrail test datasets with positive and negative cases for each
  rule.
- `validate_rules.py` — static schema and policy validation for every rule.
- `test_rules.py` — behavioural unit tests that evaluate rule logic against the
  datasets.
- `deploy_rules.py` — deployment tool with a dry-run default and a stubbed
  RunReveal sync.
- Validation workflow that runs on every pull request.
- Deployment workflow that syncs rules on merge to `main`, using a scoped
  `production` environment secret.
- Release workflow that tags and publishes a GitHub release when `VERSION`
  changes.
- Branch protection requiring pull requests and a passing `validate` check.
