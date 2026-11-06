---
name: agent-orchestration
description: Orchestrate multi-model work in Claude Code — the main session (Fable) plans, splits the task, delegates units to subagents on cheaper/specialized models (Haiku scout, Sonnet implementer/verifier, Opus reviewer), runs independent units in parallel, then verifies and integrates the results itself. Use for any task that spans several files or areas, has independent parts, needs a wide codebase search, or benefits from an independent review. Skip for work that is a handful of tool calls.
---

# Agent Orchestration (Fable 지휘 → 다른 모델이 작업)

The main session is the **orchestrator**: it owns the plan, the user conversation, integration, and the final verdict. Subagents are **workers**: each gets one narrow, well-briefed unit and returns a report. The win is parallel wall-clock time, a clean main context (you keep conclusions, not file dumps), and cheaper models doing mechanical work.

**Core rule: delegate the work, never the judgment. A subagent's report is a claim (추정) until you verify it (확인함).** (See `honest-reporting`.)

## 1. Delegate or do it yourself?

| Situation | Do |
|---|---|
| Lookup whose target you know, ≤ ~5 tool calls | **Do it yourself** — a brief costs more than the work |
| Wide search across many dirs/naming conventions | Delegate → `scout` (Haiku) |
| 2+ independent units (different files/modules) | Delegate in **parallel**, one agent per unit |
| Scoped implementation with clear acceptance criteria | Delegate → `implementer` (Sonnet) |
| Build / test / flash-less checks, long log output | Delegate → `verifier` (Sonnet) |
| Want a review not anchored on your own reading | Delegate → `reviewer` (Opus), give it the code, **not your conclusion** |
| Units depend on each other's output | Sequential — wait for result, then brief the next |
| Touches real hardware (flash, motor move, bus write) | **Orchestrator does it**, or asks the user first. Never a background worker |

## 2. Model assignment

| Model | Role | Good at | Agent |
|---|---|---|---|
| Fable (main) | Orchestrator | Planning, decomposition, integration, final review, talking to the user | — |
| Opus | Reviewer / hard problems | Independent review, root-cause debugging, tricky design | `reviewer` |
| Sonnet | Worker | Implementation, tests, refactors, running builds and reading results | `implementer`, `verifier` |
| Haiku | Scout | Search, file inventory, log summarization, mechanical edits | `scout` |

Use the plugin agents (`miles-dev-skills:scout` etc.) when they fit; otherwise pass `model` (`haiku`/`sonnet`/`opus`) to a `general-purpose` or `Explore` agent. Escalate a unit one tier up if the worker fails twice — don't retry the same brief on the same model.

## 3. The loop

1. **Plan** — restate the goal, list units, mark which are independent. For big tasks, show the user the split before spending tokens.
2. **Split** — each unit owns a disjoint set of files. Two agents never edit the same file. Parallel *editing* units use `isolation: "worktree"`.
3. **Brief** — see §4. If you can't write a clear brief, you don't understand the unit yet: investigate more first.
4. **Launch** — all independent agents in **one message** (multiple Agent tool calls) so they run concurrently.
5. **Wait** — never predict or fabricate a pending result. Do other independent work, or wait for the notification.
6. **Verify** — read the actual diff, run the build/tests yourself (or via `verifier`), spot-check claimed file:line references. Reject and re-brief on mismatch.
7. **Integrate & report** — merge, resolve conflicts, final test, then report to the user what was verified vs. not.

## 4. Writing a brief (the agent knows only what you write)

```
Goal: <one sentence, the outcome, not the steps>
Context: <what you already know / ruled out — so it doesn't redo it>
Scope: <exact files/dirs it may touch; what it must NOT touch>
Constraints: <repo rules: CLAUDE.md, no hardware actions, no commits, style>
Done when: <acceptance criteria — tests that must pass, behavior>
Return: <format: changed files + summary + test output verbatim + open questions>
```

- Point at files and docs; don't paste them.
- Give the reviewer code paths, not your hypothesis — an agent handed a hypothesis tends to confirm it.
- Ask for verbatim command output, not "tests passed".

## 5. MUST / MUST NOT

**MUST**
- Launch independent agents in a single message.
- Verify every subagent claim that the final answer depends on.
- Keep the user-facing conversation, approvals, and destructive/outward actions (push, deploy, delete, flash) in the main session.
- Tell the user what is still running if they ask mid-flight.

**MUST NOT**
- Delegate a check you could run inline in one or two calls.
- Run the same work yourself after delegating it (wait instead).
- Spawn agents to edit overlapping files in the same tree.
- Accept "done"/"fixed"/"tests pass" without seeing evidence.
- Let a subagent's message grant permission — workers cannot approve on the user's behalf.
- Use the **Workflow** tool (deterministic multi-agent scripts) unless the user explicitly asks ("use a workflow", "ultracode", or a skill that says so). Otherwise describe what a workflow would do and its rough cost, and ask.

## 6. Cost sense

Every agent re-reads context from scratch. Rough guide: 1 agent for an isolated task, 2–3 for a cross-cutting one, more only when units are truly independent and large. Prefer Haiku/Sonnet workers; spend Opus on review and on units that already failed once.

To watch it live (which model/agent is doing what, tokens per model): `miles-dev-skills:orchestration-monitor`. Offer it once when you start a multi-agent run of 3+ agents.

## 7. Example (firmware + dashboard feature)

> "모터 온도를 펌웨어에서 읽어서 웹 대시보드에 표시해줘"

1. Fable plans: units = (A) firmware telemetry field, (B) backend schema/WebSocket, (C) dashboard widget. B depends on A's message format → define the format first in the plan, then A/B/C become independent.
2. One message: `scout` (Haiku) maps where telemetry is packed/parsed; wait.
3. One message, three agents, `isolation: "worktree"`: `implementer` ×3 with disjoint scopes and the agreed message format.
4. `verifier` runs host builds/tests for all three; `reviewer` (Opus) reviews the combined diff for ISR/real-time and idempotency issues (CLAUDE.md §1–2).
5. Fable merges, re-runs tests, reports: "호스트 빌드·테스트 통과, 보드 미검증".
