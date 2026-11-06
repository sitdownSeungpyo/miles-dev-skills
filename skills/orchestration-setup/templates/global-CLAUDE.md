<!-- miles-orchestration:start -->
## Orchestration mode (miles-dev-skills)

The main session is the orchestrator (default model: Fable). For any task that spans several files or areas, has independent parts, needs a wide search, or benefits from an independent review, follow the `miles-dev-skills:agent-orchestration` skill:

- Plan and split into units with disjoint file scopes; launch independent units in parallel in one message.
- Workers: `miles-dev-skills:scout` (Haiku, search), `miles-dev-skills:implementer` (Sonnet, code), `miles-dev-skills:verifier` (Sonnet, build/test), `miles-dev-skills:reviewer` (Opus, independent review).
- Treat every subagent report as unverified until you check the diff/output yourself.
- Do small lookups (a handful of tool calls) yourself — don't delegate them.
- Keep user approvals, hardware actions, pushes, deploys, and deletes in the main session.
- Use the Workflow tool only when the user explicitly asks for one.
<!-- miles-orchestration:end -->
