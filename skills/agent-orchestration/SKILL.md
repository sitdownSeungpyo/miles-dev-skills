---
name: agent-orchestration
description: Load at the start of any multi-step session. Orchestrate multi-model work in Claude Code on top of oh-my-claudecode (OMC) — the main session (Fable) only orchestrates; implementation goes to executor on Opus, search/docs to Haiku, evidence to Sonnet, and every Agent call passes `model`. The main session picks the right OMC workflow (plan/ralplan/deep-interview → execute/team/autopilot/ralph → review → verify), routes units to OMC agents (explore/writer=Haiku, verifier=Sonnet, executor/debugger/architect/code-reviewer/critic=Opus), and adds miles hardware-safety rules plus the hw-safety-reviewer gate for firmware/robot changes. Use for any task that spans several files or areas, has independent parts, needs a wide search, or benefits from an independent review. Skip for work that is a handful of tool calls.
---

# Agent Orchestration (Fable 지휘 + OMC 워크플로 + 하드웨어 안전 규칙)

The main session is the **orchestrator** (default model: the `fable` alias set by orchestration-setup; the user may have switched models with `/model`). It owns the plan, the user conversation, approvals, integration, and the final verdict — and little else. **The main model does not do the work**: in Claude Code everything the main session reads or edits itself is billed to and done by the main model, so a Fable session that implements is a Fable session, and OMC adds nothing. The working model is **Opus** (executor/debugger); Haiku and Sonnet take what they are good enough for. **oh-my-claudecode (OMC)** supplies the workflows and the specialist agents; this skill decides *which* to use and adds the rules OMC doesn't know about — this codebase drives real hardware.

**Core rules**
1. Delegate the work, never the judgment. A subagent report is 추정 until you verify it (확인함). (`honest-reporting`)
2. One loop authority per session (OMC rule): don't run `ralph`, `autopilot`, `team`, `/goal` at the same time.
3. Physical actions — flash, motor/actuator command, bus write to a live device, deploy, OTA, push — stay in the main session with user approval. No OMC worker or loop does them.
4. **Use every tier, every session.** The point of this setup is that Haiku and Sonnet do the work they are good enough for, and the main model keeps the judgment. A session where the main model did all of it is the failure mode this rule exists for (2026-11-08: a whole working day ran on Opus alone — every search, edit and review — and the user noticed). So:
   - Load this skill at the **start** of any multi-step session, not once the work is done.
   - Every Agent call names the OMC/miles agent **and passes `model`** explicitly (§2's column). Without it the call may be labelled `inherit`.
   - Never use `general-purpose` when OMC agents exist: it inherits the main model, so a "delegated" review ran on Opus anyway.
   - The main session does only what needs its judgment or authority: planning and splitting, reading a returned diff/report to accept or reject it, short confirmations (one read, one test run), user questions, and the main-session-only actions (hardware commands, commit, push). Anything else is delegated: code and config changes to `executor` with `model: opus`, debugging to `debugger` (opus), searches across files to `explore` (Haiku), README/docs to `writer` (Haiku), test/build evidence to `verifier` (Sonnet).
   - Before reporting a unit done, check the routing: which agent and model did the search, the edit, the review? If the answer is "main model" for all three, delegate the next unit.

If OMC is not installed (`oh-my-claudecode:*` agents missing), use §6 fallback and offer `orchestration-setup`.

## 1. Pick the workflow

| Situation | Use | Notes |
|---|---|---|
| One read or one command to confirm something, target known | **Do it yourself** | Anything that edits code/config or spans files is delegated (rule 4) |
| Requirements vague / user unsure what they want | `/oh-my-claudecode:deep-interview` | Before any code |
| Non-trivial change, needs a plan | `/oh-my-claudecode:plan` or `ralplan` (Planner+Architect+Critic) | `ralplan --deliberate` for high-risk (firmware, safety, protocol changes) |
| Approved plan → working code | `/oh-my-claudecode:execute` | Default Tier-0 path: plan → execute → review → verify |
| 2+ independent units, larger scope | `/team` | Staged pipeline with shared task list; give each unit a disjoint file scope |
| Must not stop until verified | `ralph` | Only for host-side work with a machine-checkable done condition |
| End-to-end feature, minimal ceremony | `autopilot` | Not for firmware that needs on-target verification |
| Finished work → defects/risk | `/oh-my-claudecode:review` | + `hw-safety-reviewer` if hardware-facing (§3) |
| Quality gates (build/test/lint/typecheck) | `/oh-my-claudecode:verify` | Evidence, not "looks fine" |
| Root cause unclear | `trace` (competing hypotheses) or `debugger` agent | Pair with `hw-debug` skill for bus/board issues |
| Open question needing sources | `research` / `external-context` | |

Ask before starting `team`/`autopilot`/`ralph` on a large task: state the plan, units, and that it will spawn several agents.

## 2. Route units to agents

OMC agents run on their pinned model unless you pass `model`. Defaults:

| Need | Agent | Model |
|---|---|---|
| Find files/symbols/patterns | `oh-my-claudecode:explore` | Haiku |
| Implement a scoped unit (the main work) | `oh-my-claudecode:executor` — pass `model: opus` | **Opus** (`sonnet` for mechanical edits) |
| Build error / regression / stack trace | `oh-my-claudecode:debugger` — pass `model: opus` | **Opus** |
| Causal tracing with hypotheses | `oh-my-claudecode:tracer` | Sonnet |
| Tests, TDD, flaky tests | `oh-my-claudecode:test-engineer` | Sonnet |
| Completion evidence | `oh-my-claudecode:verifier` | Sonnet |
| UI / dashboard | `oh-my-claudecode:designer` (+ `web-frontend` / `flutter-app` skill) | Sonnet |
| Commits / history | `oh-my-claudecode:git-master` — **but follow repo CLAUDE.md commit format, no AI trailers** | Sonnet |
| Library/SDK docs | `oh-my-claudecode:document-specialist` | Sonnet |
| Architecture / design advice (read-only) | `oh-my-claudecode:architect` | Opus |
| Code review | `oh-my-claudecode:code-reviewer` | Opus |
| Security review | `oh-my-claudecode:security-reviewer` | Opus |
| Plan critique | `oh-my-claudecode:critic` / `planner` / `analyst` | Opus |
| Docs / README | `oh-my-claudecode:writer` | Haiku |
| **Firmware / robot / device-facing change review** | **`miles-dev-skills:hw-safety-reviewer`** | Opus |

Escalate a unit one tier (Haiku → Sonnet → Opus) after two failures; don't retry the same brief on the same model. Fable is not a worker tier: if Opus fails twice, re-plan the unit (smaller scope, better brief) rather than doing it in the main session.

## 3. Hardware overlay (OMC doesn't know these — always apply)

- **Gate**: any diff touching firmware, drivers, ISRs, control loops, motor/actuator commands, CAN/UART/I2C/SPI protocol, OTA, or E-stop paths must pass `miles-dev-skills:hw-safety-reviewer` before you report it done.
- **Workers never**: flash boards, send commands to live devices, run OTA, deploy to robots, push, or delete. Put this in every brief for `executor`/`team`/`autopilot`.
- **Done ≠ compiled**: for firmware, `verify` can only prove host builds/tests. Report as "호스트 빌드·테스트 통과, 보드 미검증" until on-target checks run (CLAUDE.md §6).
- **Domain skills in briefs**: tell workers which miles skill applies (`embedded-firmware`, `ros2-dev`, `hw-debug`, `platformio-arduino`, `api-backend`, `web-frontend`, `flutter-app`, `robot-deploy`).
- **Commit format**: repo CLAUDE.md §7 wins over OMC/git-master defaults (Korean `[tag]` subject, no AI trailers).

## 4. Brief template (the agent knows only what you write)

```
Goal: <outcome, one sentence>
Context: <what you know / ruled out>
Scope: <files/dirs it may touch; what it must NOT touch>
Constraints: <repo CLAUDE.md; miles skill to follow; no flash/device/deploy/push/commit>
Done when: <tests/behavior that must hold>
Return: <changed files + summary + verbatim command output + open questions>
```

Give reviewers code paths, not your hypothesis. Ask for verbatim output, not "tests passed".

## 5. Verify and report

1. Read the actual diff; run build/tests yourself or via `verifier` — never self-approve in the same context (OMC rule).
2. Check for fake completion: TODO stubs, `test.skip`/`.only`, unimplemented branches → blockers.
3. Hardware-facing → `hw-safety-reviewer` result attached.
4. Report what was verified vs. not, scoped ("보드 미검증").

Monitoring: OMC HUD (status line) for the one-line summary; `miles-dev-skills:orchestration-monitor` for the detailed per-agent/model/token GUI. Offer it once when starting a run of 3+ agents.

## 6. Fallback without OMC

Use the Agent tool with `subagent_type: general-purpose` (or `Explore` for search) and pass `model: haiku|sonnet|opus` per §2's model column. Same briefs, same rules. Use the **Workflow** tool only if the user explicitly asks for a workflow.

## 7. Example — "모터 온도를 펌웨어에서 읽어서 웹 대시보드에 표시해줘"

1. `ralplan` → plan with units: (A) firmware telemetry field, (B) backend schema/WebSocket, (C) dashboard widget, plus the message format agreed up front.
2. `explore` (Haiku) maps where telemetry is packed/parsed.
3. `/team` with 3 units, disjoint scopes, briefs naming `embedded-firmware` / `api-backend` / `web-frontend` and "no flashing".
4. `verify` on host builds/tests; `code-reviewer` on the full diff; `hw-safety-reviewer` on (A).
5. Fable merges, reports "호스트 빌드·테스트 통과, 보드 미검증", asks the user before flashing.
