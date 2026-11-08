<!-- miles-orchestration:start -->
## miles-dev-skills overlay (on top of oh-my-claudecode)

The main session (default model: Fable) orchestrates. Use OMC workflows and agents, choosing them per `miles-dev-skills:agent-orchestration`:

- Default path: `plan`/`ralplan` → `execute` (or `/team` for 2+ independent units) → `review` → `verify`. `deep-interview` first when requirements are vague. One loop authority per session.
- The main session (Fable) orchestrates and judges; it does not implement. Only one-read/one-command confirmations, user questions, and main-session-only actions (hardware, commit, push) happen there.
- **Use every tier:** load `miles-dev-skills:agent-orchestration` at the start of multi-step work; route searches to `explore` (Haiku), docs to `writer` (Haiku), implementation to `executor` and debugging to `debugger` with `model: opus` (Opus is the working model), evidence to `verifier` (Sonnet), reviews to `code-reviewer`/`hw-safety-reviewer` (Opus). Pass `model` on every Agent call; never `general-purpose` (it inherits the main model).
- Treat every subagent report as unverified until you check the diff/output yourself.
- **Hardware overlay (overrides OMC defaults):** flashing, live-device commands, OTA, robot deploys, pushes and deletes stay in the main session with user approval — never in `executor`/`team`/`autopilot`/`ralph`. Device-facing diffs (firmware, drivers, ISRs, control loops, bus protocols, E-stop, OTA) must pass `miles-dev-skills:hw-safety-reviewer`. Report firmware as "호스트 검증만, 보드 미검증" until tested on target.
- Commits follow the repo's CLAUDE.md format (no AI trailers) even when `git-master` is used.
- Detailed agents/models/tokens GUI: `miles-dev-skills:orchestration-monitor` ("모니터 띄워줘"); OMC HUD is the one-line status.
<!-- miles-orchestration:end -->
