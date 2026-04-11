---
description: Create a Conventional Commit following SAHOOL git workflow
---

Create a git commit following the SAHOOL conventional-commits standard defined in `CLAUDE.md`.

## Steps

1. Run these commands in parallel:
   - `git status` (without `-uall`) to see untracked files
   - `git diff` (staged + unstaged) to see the changes being committed
   - `git log --oneline -5` to match this repo's commit-message style

2. Analyze the staged changes and draft a commit message using the Conventional Commits spec:
   - `feat:` new user-facing feature
   - `fix:` bug fix
   - `docs:` docs-only change
   - `test:` test-only change
   - `refactor:` code restructure with no behavior change
   - `chore:` tooling / dependency / CI change
   - `perf:` performance improvement
   - `build:` build-system change (Docker, Makefile)
   - `ci:` GitHub Actions / ArgoCD change

3. Scope examples for this monorepo:
   - Backend Python service: `feat(field-management): …`, `fix(yolo26-vision): …`
   - Node.js service: `feat(user-service): …`
   - Shared module: `feat(shared/ai): …`, `fix(shared/auth): …`
   - Frontend app: `feat(web): …`, `fix(admin): …`, `feat(mobile): …`
   - Infrastructure: `chore(docker): …`, `ci(workflows): …`
   - Contracts: `feat(contracts): …` (bump `CONTRACT_VERSION` in the same commit)

4. **Never** commit files that likely contain secrets: `.env`, `credentials.json`, `*.pem`, `config/certs/*.key`. Warn the user if the diff touches them.

5. **Never** stage everything with `git add -A`. Stage specific files by name.

6. Use a HEREDOC to pass the commit message so the formatting survives:

   ```
   git commit -m "$(cat <<'EOF'
   <type>(<scope>): <short subject in imperative mood>

   <optional body explaining the "why", not the "what">

   https://claude.ai/code/session_<session-id>
   EOF
   )"
   ```

7. After the commit completes, run `git status` to verify the working tree is clean.

## SAHOOL-specific Guards

- If the commit touches `packages/shared-types/src/contracts/*`, remind the user to bump `CONTRACT_VERSION` and run `npx tsx scripts/sync-contracts-to-dart.ts`.
- If the commit touches a Dockerfile under `apps/services/*/Dockerfile`, remind the user that 3-tier mirror fallback (Pattern A) is the recommended pattern.
- If the commit touches `governance/services.yaml` or `governance/agents.yaml`, remind the user that this is the single source of truth and CI will validate it.
- If the commit touches any deprecated service in `archive/deprecated-services/`, reject the commit — deprecated services are frozen.

## Do NOT

- Do NOT run `git push` as part of this command — pushing is a separate explicit action.
- Do NOT amend previous commits unless the user explicitly asked.
- Do NOT use `--no-verify`, `--no-gpg-sign`, or any hook-skipping flag.
