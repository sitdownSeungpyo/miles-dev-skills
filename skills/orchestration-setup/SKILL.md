---
name: orchestration-setup
description: Set up the full orchestration environment on this PC (macOS, Linux, or Windows) — clone/update miles-dev-skills, install the miles-dev-skills plugin and oh-my-claudecode (OMC), run OMC's CLAUDE.md coordinator and HUD status line setup, set Fable as the default main-session model, and add the miles hardware-safety overlay block to ~/.claude/CLAUDE.md. Idempotent. Use when the user asks to set up orchestration, install miles-dev-skills or OMC, or "SETUP.md 읽고 셋업해줘" on a new machine.
---

# Orchestration Setup (miles-dev-skills + oh-my-claudecode)

Run in order. **Every step checks first and skips if already done** — re-running must be safe. Report each step as 완료 / 건너뜀(이미 됨) / 실패 (+ verbatim output). Never claim a step worked without its check output.

| Item | Value |
|---|---|
| miles repo | `git@github.com:sitdownSeungpyo/miles-dev-skills.git` (HTTPS fallback `https://github.com/sitdownSeungpyo/miles-dev-skills`) |
| miles plugin | `miles-dev-skills@miles-dev-skills` |
| OMC repo | `https://github.com/Yeachan-Heo/oh-my-claudecode` (MIT) |
| OMC plugin | `oh-my-claudecode@omc` (marketplace name `omc`) |

Before any change to `~/.claude/CLAUDE.md` or `~/.claude/settings.json`, back them up to `<file>.bak-<YYYYMMDD>` (skip if that backup already exists today).

## 0. Preflight

- `claude --version`; `claude plugin --help` must list `marketplace`, `install`, `update`, `details`. Otherwise tell the user to update Claude Code and stop.
- `git --version`, `node --version` (OMC hooks and HUD need Node; if missing, ask the user to install Node LTS and stop at step 3).
- Detect OS. On Windows `~` = `%USERPROFILE%`; use PowerShell equivalents and forward slashes in `statusLine` commands.
- tmux is **optional** (only for OMC's `omc team` CLI workers). Don't install it unless the user asks.

## 1. miles-dev-skills repo (= `$REPO`)

1. If cwd (or a parent) has `.claude-plugin/marketplace.json` with `"name": "miles-dev-skills"` → `$REPO`.
2. Else `claude plugin marketplace list` → use the registered directory if it exists.
3. Else ask where to clone (suggest `~/miles-dev-skills`) and `git clone`.

Existing repo: `git -C $REPO status --short` — clean → `git pull --ff-only`; dirty → don't pull, tell the user.

## 2. Install/update both plugins

```bash
claude plugin marketplace list
# miles
claude plugin marketplace add "$REPO"                                   # if missing
claude plugin marketplace update miles-dev-skills
claude plugin install miles-dev-skills@miles-dev-skills                 # or: plugin update …
# OMC
claude plugin marketplace add https://github.com/Yeachan-Heo/oh-my-claudecode   # if 'omc' missing
claude plugin marketplace update omc
claude plugin install oh-my-claudecode@omc                              # or: plugin update …
```

Check: `claude plugin details miles-dev-skills@miles-dev-skills` → skills incl. `agent-orchestration`, `orchestration-monitor`, `orchestration-setup` and agent `hw-safety-reviewer`. `claude plugin details oh-my-claudecode@omc` → ~19 agents, hooks loaded.

## 3. OMC setup (equivalent of `/oh-my-claudecode:omc-setup --global`, scripted)

Let `$OMC` = the newest version dir under `~/.claude/plugins/cache/omc/oh-my-claudecode/` (numeric sort).

1. **CLAUDE.md** (OMC's own coordinator; it backs up and keeps content outside its `<!-- OMC:START/END -->` markers as "User customizations"):
   ```bash
   CLAUDE_PLUGIN_ROOT="$OMC" bash "$OMC/scripts/setup-claude-md.sh" global overwrite
   ```
   Skip if `~/.claude/CLAUDE.md` already has `<!-- OMC:VERSION:<same version> -->`.
2. **HUD** — follow `$OMC/skills/hud/SKILL.md` "setup" steps exactly (copy from the canonical template, don't write inline):
   ```bash
   mkdir -p ~/.claude/hud/lib
   cp "$OMC/scripts/lib/hud-wrapper-template.txt" ~/.claude/hud/omc-hud.mjs
   cp "$OMC/scripts/lib/config-dir.mjs" ~/.claude/hud/lib/config-dir.mjs
   chmod 755 ~/.claude/hud/omc-hud.mjs            # skip on Windows
   ```
   Then set `statusLine` in `~/.claude/settings.json` (JSON-aware edit, keep every other key):
   `{"type":"command","command":"node ${CLAUDE_CONFIG_DIR:-$HOME/.claude}/hud/omc-hud.mjs"}` — on Windows use the absolute forward-slash path. If the user already has a different `statusLine`, ask before replacing it.
   Check: `echo '{}' | node ~/.claude/hud/omc-hud.mjs` prints an `[OMC#…]` line.
3. `node "$OMC/scripts/repair-plugin-cache.mjs"`
4. Not done here (offer only): OMC npm CLI (`npm i -g oh-my-claude-sisyphus`) and tmux for `omc team`; notification integrations (`/oh-my-claudecode:configure-notifications`).

## 4. Default model = Fable

- Read `~/.claude/settings.json`. `"model": "fable"` already → skip. Keep the alias, not a pinned ID, so a new Fable release needs no settings change. Don't write the resolved release into docs; if the user asks which release it is, read the model ID the running session reports.
- Otherwise confirm with the user (Fable is the most expensive tier; it is the orchestrator, OMC agents run on their pinned Haiku/Sonnet/Opus).
- `jq '.model = "fable"'` to a temp file → validate → move. Preserve all other keys (hooks, statusLine, permissions, env).

## 5. miles overlay block in `~/.claude/CLAUDE.md` (must run **after** step 3)

Source: `$REPO/skills/orchestration-setup/templates/global-CLAUDE.md`.
- File has `<!-- miles-orchestration:start -->` → replace through `<!-- miles-orchestration:end -->` with the template.
- Else append it after the `<!-- OMC:END -->` block. Never touch content inside OMC markers.

## 6. Verify and report

```bash
claude plugin details miles-dev-skills@miles-dev-skills | head -8
claude plugin details oh-my-claudecode@omc | sed -n 1,9p
jq '{model, statusLine}' ~/.claude/settings.json
grep -cE 'OMC:START|OMC:END|miles-orchestration:(start|end)' ~/.claude/CLAUDE.md   # → 4
claude -p --model haiku "List only subagent type names starting with oh-my-claudecode: or miles-dev-skills:, one per line."
```

Tell the user to **start a new Claude Code session** (current session keeps its model, plugins and CLAUDE.md). HUD appearance and real `team`/`autopilot` runs are 미검증 until they try them.

## Rollback

- `claude plugin uninstall oh-my-claudecode@omc` (and/or `miles-dev-skills@miles-dev-skills`)
- Restore `~/.claude/settings.json` and `~/.claude/CLAUDE.md` from the `.bak-*` files (OMC also leaves `CLAUDE.md.backup.<timestamp>`)
- `rm -rf ~/.claude/hud` if the HUD was installed by this setup
- Temporary disable without uninstall: env `DISABLE_OMC=1`
