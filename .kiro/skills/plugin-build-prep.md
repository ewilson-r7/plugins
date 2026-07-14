# Plugin Build Prep (Pre-Build Readiness)

Run this **before** any build/update/enhance work. It ensures tooling is installed and current and that you build against the latest SDK.

## When to Use
- Before `insight-plugin create` (new plugin)
- Before `insight-plugin refresh` (new action/trigger/task or spec change)
- Any time you're about to write plugin code

Skip for review/question (read-only) work.

## Steps

### 1. Confirm target repo
Confirm the build intent and the explicit **prod or dev** choice (never infer from the working directory):
- **prod** → `~/Documents/GitHub/insightconnect-plugins/plugins/<name>`
- **dev** → `~/Documents/GitHub/plugins/plugins/<name>`

See `repos.md` for the full routing table.

### 2. Verify tooling is installed and current
```bash
insight-plugin --version     # install/upgrade via pipx or pip if missing
prospector --version
black --version
docker --version             # required for insight-plugin validate (DockerValidator)
pyenv versions               # confirm the SDK's target Python is installed
```
If `insight-plugin` is missing or outdated:
```bash
pipx upgrade insight-plugin || pipx install insight-plugin
# or: pip install --upgrade insight-plugin
```
Offer to install/upgrade anything missing before proceeding.

### 3. Resolve the latest SDK version from the SDK README
The latest `insightconnect-plugin-runtime` version is the **top entry** under `## Changelog` in:
```
~/Documents/GitHub/komand-plugin-sdk-python/README.md
```
Read that file, take the highest/newest version at the top of the changelog list, and use it for `sdk.version` in `plugin.spec.yaml`. The same README states the target Python version (currently 3.13.x).

**Do not hardcode SDK or Python versions** — always read them fresh from this README at build time, since it is updated with each SDK release.

### 4. Set the Python version for tooling
Resolve the installed 3.13.x pyenv version with `pyenv versions` (do not hardcode) and use it for all commands. Below, `3.13.x` stands in for that resolved version:
```bash
PYENV_VERSION=3.13.x insight-plugin refresh
PYENV_VERSION=3.13.x insight-plugin validate
PYENV_VERSION=3.13.x prospector icon_<plugin_name>/
```
If the SDK README targets a newer 3.13.x than what's installed, offer:
```bash
pyenv install 3.13.<x>
```

### 5. Proceed
Only after tooling is confirmed and the latest SDK version is known, continue to `create-new-plugin` or `create-plugin-action`.

## Checklist
- [ ] Prod vs dev confirmed explicitly (not inferred from cwd)
- [ ] `insight-plugin`, `prospector`, `black`, `docker` present and current
- [ ] Target Python (3.13.x) installed via pyenv
- [ ] Latest SDK version read from `komand-plugin-sdk-python/README.md` changelog
- [ ] `sdk.version` in the spec set to that latest version
