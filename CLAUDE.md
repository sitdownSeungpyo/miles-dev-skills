# CLAUDE.md

Behavioral guidelines for robotics, embedded, web, and app development. Merge with project-specific instructions as needed. Detailed domain knowledge lives in `skills/` — these are the cross-cutting rules that apply everywhere.

**Tradeoff:** These guidelines bias toward safety and verification over speed. Code here often drives physical hardware; a wrong guess can brick a board or move a robot. For pure-software throwaway scripts, use judgment.

## 1. Hardware Is Unforgiving

**Never assume the happy path when code touches physical devices.**

- Check every HAL/driver/bus return code. No silent failures on hardware.
- Commands that trigger physical actions (motor move, actuator fire) must be idempotent or deduplicated — a retried request must not execute twice.
- E-stop and safety-critical UI is never optimistic: reflect only acknowledged state.
- Timeout every blocking wait on a peripheral or network peer. Plan the recovery path (bus reset, reconnect, watchdog) at design time, not after the first field failure.

## 2. Real-Time Paths Stay Clean

**ISRs and control loops do the minimum; everything else is deferred.**

- ISRs: set a flag or push to a queue, return. No printf, no blocking, no allocation.
- `volatile` (or atomics) for anything shared between ISR and main context.
- No dynamic allocation in real-time paths after init. Static by default.
- UI rendering high-rate telemetry: buffer in the data layer, flush at 10–15 Hz — never re-render per message.

## 3. Debug Layer by Layer

**Narrow the problem: power → clock → electrical → protocol → logic. Never guess-and-flash repeatedly.**

- First questions: did this ever work? What changed last? Reproducible or intermittent?
- One hypothesis, one test at a time. Pick the cheapest test that splits the possibility space.
- Report as: observed symptom → layer isolated → evidence → most likely cause → next test.
- Intermittent failures → suspect power, ground, EMI, race conditions before logic bugs.

## 4. Design for Disconnection

**Every link — serial, BLE, WebSocket, MQTT — will drop. Behavior on drop is a design decision, not an accident.**

- Connections are state machines (connecting → ready → lost → reconnecting) surfaced to the user.
- Auto-reconnect with exponential backoff + jitter; heartbeats detect silent death.
- Devices report presence (heartbeat/LWT); servers mark them stale, never assume alive.
- Every async view designs loading / empty / error / disconnected states — not just success.

## 5. Ship with a Rollback Path

**A deploy you can't undo is a gamble, not a release.**

- OTA firmware: A/B slots, signed images with production keys, post-boot self-test with automatic rollback. No exceptions.
- Staged rollout: bench → canary robot → fleet. Never fleet-wide in one step.
- Version every protocol between firmware, backend, and app; newer code tolerates older peers.
- Rollback paths are tested, not just present.

## 6. Verify on Target

**Compiling is not working. Measure before claiming.**

- Firmware success criteria run on the board: timing asserted with GPIO + logic analyzer, stack high-water marks checked, watchdog proven.
- Measure before optimizing: `.map` files and profilers for size/speed, React Profiler for renders, `ros2 topic hz` for rates. No optimization without a number before and after.
- Unit test hardware-independent logic on host; keep the on-target test list short and meaningful.
- Match the project's existing stack and style — check `package.json` / `platformio.ini` / `package.xml` before introducing anything new.


## 7. Commit Convention

**Follow this message format for every commit:**

```
[태그] 한 줄 요약 — 세부 변경 사항을 쉼표로 나열
```

Example:

```
[fix] 전면 개선 — Profile Check 복구, QC 안전/판정 로직 수정, 빌드 단일화
```

- Tags: `[feat]` new feature, `[fix]` bug fix, `[refactor]` restructuring, `[docs]` documentation, `[test]` tests, `[build]` build/CI, `[chore]` maintenance.
- Subject line in Korean, imperative tone, ≤ 72 chars; add a body only when the "why" isn't obvious from the diff.
- **Never add Claude/AI trailers or attribution** to commits or any update-related work: no `Co-Authored-By: Claude ...`, no `Claude-Session: ...`, no `Generated with Claude Code` lines — in commit messages, PR bodies, tags, or release notes.

---

**These guidelines are working if:** field failures have designed recovery paths instead of hotfixes, debugging sessions converge instead of thrashing, deploys are boring, and diffs stay small and traceable to the request.
