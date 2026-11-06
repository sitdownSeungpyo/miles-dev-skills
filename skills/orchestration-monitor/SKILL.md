---
name: orchestration-monitor
description: Open a local web GUI that shows which models and subagents are working right now (main session + each subagent, its model, status, last action) and token usage per model/session (input, output, cache read/write). Use when the user asks to monitor orchestration, see what agents/models are doing, check token usage, or "모니터 띄워줘" / "토큰 사용량 보여줘". Opens as a split pane inside cmux, otherwise in the default browser.
---

# Orchestration Monitor (모델·서브에이전트 작업 현황 + 토큰 GUI)

Complements the oh-my-claudecode HUD: the HUD is a one-line status bar (rate limits, context, session); this monitor is the detailed view — every session and subagent (OMC agents included), its model, status, last action, and tokens.

A stdlib-only Python server (`monitor.py` + `monitor.html` in this skill's directory) that reads Claude Code transcripts under `~/.claude/projects/` **read-only** and serves a dashboard on `http://127.0.0.1:8765/` (localhost only), refreshing every 3 s.

## Launch

Run with the skill's base directory (shown when this skill loads) as `$DIR`:

```bash
python3 -I "$DIR/monitor.py" --launch            # start detached if not running, then open
python3 -I "$DIR/monitor.py" --launch --port 8766 # if 8765 is taken by something else
```

- Inside cmux (`$CMUX_WORKSPACE_ID` set): opens in a cmux browser split next to the terminal.
- Elsewhere: opens the default browser. Windows: use `py -3` or `python` instead of `python3`.
- `--launch` is idempotent — if the server already answers, it just opens the page.
- Report the URL and how to stop it to the user. Do not leave it running silently if they only wanted a one-off look — ask.

Other modes: `--dump` prints the JSON once (no server, good for a quick text answer); `--hours N` sets the default window; `--claude-dir` points at a non-default config dir (defaults to `$CLAUDE_CONFIG_DIR` or `~/.claude`).

Stop: macOS/Linux `pkill -f orchestration-monitor/monitor.py`; Windows: end the `python` process in Task Manager.

## What it shows

| Area | Content |
|---|---|
| KPI tiles | total tokens, cache read/write, active sessions, running subagents |
| 모델별 토큰 | bar + table per model (Fable/Opus/Sonnet/Haiku have fixed colors) |
| 세션 cards | title, cwd, model mix bar, main session's last tool action |
| 서브에이전트 table | agent type, task description, model(s), status (실행 중/대기/완료), tokens, last tool action |

## How numbers are computed (say this if the user asks about accuracy)

- Source: each transcript's assistant records → `message.usage`. Records repeat per content block, so usage is **deduplicated by `message.id`**.
- Subagents: `<session>/subagents/agent-*.jsonl` + `.meta.json` (`agentType`, `description`, `finished`).
- Status: `finished:true` → 완료; `finished:false` → 실행 중 if written in the last 90 s, else 대기 (usually a long tool call).
- **Tokens only — no cost.** Prices are not hard-coded because they change; if the user wants cost, look up current pricing (claude-api skill) and compute it from the table, labeled as an estimate.
- The transcript format is internal to Claude Code and may change between versions. If numbers look wrong, run `--dump` and inspect a transcript before trusting the GUI.
