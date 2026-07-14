---
inclusion: auto
---
# Plugin Repositories & Routing

There are several local clones of Rapid7 plugin repos. Which one you use depends on the **intent** of the request and, for builds, on an explicit **prod vs dev** choice. **Never infer prod vs dev from the current working directory — always ask or use what the user stated.**

## Routing Table

| Intent | Target | Path | Git origin | Workflow |
|--------|--------|------|------------|----------|
| Build / Update / Enhance | **prod** | `~/Documents/GitHub/insightconnect-plugins/plugins/<name>` | `rapid7/insightconnect-plugins` | Full release flow (`git-workflow.md`) |
| Build / Update / Enhance | **dev** | `~/Documents/GitHub/plugins/plugins/<name>` | `ewilson-r7/plugins` (personal repo; upstream rapid7) | Commit to `main` (below) |
| Review / Question | current | `~/Documents/GitHub/insightconnect-plugins/plugins/<name>` | `rapid7/insightconnect-plugins` | Read-only |
| Review / Question | legacy | `~/Documents/GitHub/komand-plugins/plugins/<name>` | rapid7 (legacy) | Read-only |
| SDK version lookup | — | `~/Documents/GitHub/komand-plugin-sdk-python/README.md` (`## Changelog`) | rapid7 | Read top entry |

## Rules

1. **Build / Update / Enhance** always requires an explicit **prod or dev** answer. If the user didn't say, ask. Do not guess and do not read it from the working directory.
2. **Review / Question** is **read-only** and always uses a **master** repo:
   - Check `insightconnect-plugins` first (current plugins).
   - Fall back to `komand-plugins` for legacy plugins.
   - Never review from the `plugins` fork — it may contain uncommitted local changes.
3. If a review turns into a fix, stop and re-enter build intent (ask prod or dev) before writing anything.
4. Before any build, run the **pre-build readiness** step (`plugin-build-prep` skill): verify tooling and pull the latest SDK version from the SDK README changelog.

## Dev Repo Workflow (lightweight)

For **dev** builds on the personal repo (`ewilson-r7/plugins`):

All plugins live on `main` in `plugins/<plugin_name>/`. No feature branches needed for dev work — commit directly to `main`:
```bash
# Make changes in plugins/<plugin_name>/
git add plugins/<plugin_name>/
git commit -m "plugin_name: Short description"
git push origin main
```

When ready to submit upstream as a PR:
```bash
git fetch upstream
git checkout -b feature/<plugin>-<short-desc> upstream/master
# copy or cherry-pick the plugin changes
git push -u origin feature/<plugin>-<short-desc>
# open PR against rapid7/insightconnect-plugins master
```

Reserve the full release-branch flow (`git-workflow.md`) for **prod** builds on `insightconnect-plugins`.
