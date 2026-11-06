---
name: orchestration-setup
description: Set up the miles-dev-skills orchestration environment on this PC (macOS, Linux, or Windows) — clone/update the miles-dev-skills repo, register it as a local plugin marketplace, install/update the plugin (skills + scout/implementer/reviewer/verifier subagents), set Fable as the default main-session model, and add the orchestration block to the user-level ~/.claude/CLAUDE.md. Idempotent. Use when the user asks to set up orchestration, install miles-dev-skills, or "SETUP.md 읽고 셋업해줘" on a new machine.
---

# Orchestration Setup (어느 PC에서든 동일하게)

Run these steps in order. **Every step checks first and skips if already done** — re-running must be safe. Report each step as 완료 / 건너뜀(이미 됨) / 실패(+ verbatim output). Never claim a step worked without its check output.

Repo: `https://github.com/sitdownSeungpyo/miles-dev-skills` (SSH: `git@github.com:sitdownSeungpyo/miles-dev-skills.git`)
Plugin id: `miles-dev-skills@miles-dev-skills`

## 0. Preflight

- `claude --version` — record it. `claude plugin --help` must list `marketplace`, `install`, `update`, `details`. If not, tell the user to update Claude Code and stop.
- Detect OS. Paths below use `~`; on Windows, `~` = `%USERPROFILE%` and use PowerShell equivalents.
- `git --version` must work.

## 1. Locate or clone the repo (= `$REPO`)

1. If the current directory (or a parent) contains `.claude-plugin/marketplace.json` with `"name": "miles-dev-skills"` → that is `$REPO`.
2. Else check `claude plugin marketplace list` — if `miles-dev-skills` is registered with a directory source that exists, use that path.
3. Else ask the user where to clone (suggest `~/miles-dev-skills`) and `git clone` (try SSH, fall back to HTTPS).

If `$REPO` exists: `git -C $REPO status --short` — if clean, `git -C $REPO pull --ff-only`; if dirty, do **not** pull; tell the user and continue with the local state.

## 2. Register marketplace + install/update plugin

```bash
claude plugin marketplace list            # is miles-dev-skills there? which path?
claude plugin marketplace add "$REPO"     # only if missing
claude plugin marketplace update miles-dev-skills
claude plugin list                        # installed already?
claude plugin install miles-dev-skills@miles-dev-skills   # if not installed (user scope)
claude plugin update  miles-dev-skills@miles-dev-skills   # if installed
```

If the marketplace is registered at a *different* path than `$REPO`, ask the user which one to keep before removing/re-adding.

Check: `claude plugin details miles-dev-skills@miles-dev-skills` lists the skills from `.claude-plugin/plugin.json` (including `agent-orchestration`, `orchestration-setup`) and the 4 agents `scout`, `implementer`, `reviewer`, `verifier`.

## 3. Default model = Fable

File: `~/.claude/settings.json` (may not exist).

- Read it first. If `"model"` is already `"fable"` → skip.
- Otherwise show the user the current value and confirm the change (Fable is the most expensive model; it is the orchestrator, workers run on cheaper models).
- Back up to `settings.json.bak-<YYYYMMDD>` before editing. Change **only** the `"model"` key — preserve hooks, permissions, env, and everything else. Use a JSON-aware edit (e.g. `jq '.model = "fable"'` to a temp file, then move), or Edit tool on the exact line.
- Check: `jq . ~/.claude/settings.json` parses, and `.model == "fable"`, and other top-level keys are unchanged vs. backup.

Model alias `fable` is accepted by `claude --model` (see `claude --help`). If a future version drops the alias, use the full model id shown in `/model`.

## 4. User-level CLAUDE.md orchestration block

File: `~/.claude/CLAUDE.md` (create if missing). Block source: `$REPO/skills/orchestration-setup/templates/global-CLAUDE.md`.

- If the file contains `<!-- miles-orchestration:start -->` → replace everything between start/end markers with the template (keeps it updated).
- Else append the template (preceded by a blank line). Never overwrite other content.

## 5. Final verification and report

- `claude plugin details miles-dev-skills@miles-dev-skills` (paste relevant lines)
- `jq .model ~/.claude/settings.json`
- `grep -c miles-orchestration ~/.claude/CLAUDE.md` → 2
- Optional smoke test (costs a little): `claude -p --model haiku "List the names of subagent types available to you that start with miles-dev-skills:"` → should include the 4 agents.

Tell the user: **start a new Claude Code session** to pick up the new default model and CLAUDE.md (the current session keeps its model). Things you could not verify (e.g. new-session model) go in the report as 미검증.

## Uninstall / rollback

- `claude plugin uninstall miles-dev-skills@miles-dev-skills`
- Restore `~/.claude/settings.json` from the `.bak-*` file
- Delete the marker block from `~/.claude/CLAUDE.md`
