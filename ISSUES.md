# Open issues

Known gaps to revisit.

## Cowork does not reliably offer to pin the Artifact on its own, despite `SKILL.md` instructing it to

Confirmed live, three separate times, across three different attempts at strengthening the instruction (prominence, restructuring into a standalone step, task-list framing): a Cowork session can score a JD and build the dashboard file correctly, then simply end its turn without ever raising the Artifacts library at all, even though `SKILL.md` instructs offering to pin it as a required part of that step. Each time, asking directly ("why didn't you create an artifact?") worked immediately and correctly. This looks like a genuine behavioural tendency – satisfying the literal request over proactively volunteering a separate action – that prompt engineering within `SKILL.md` has not reliably overridden so far.

**Mitigated, not solved:** rather than continuing to chase automatic behaviour, `README.md` now recommends the user ask for the pinned Artifact explicitly in their first message of any new Cowork chat. This works reliably when tried. `SKILL.md`'s own instruction to offer proactively is left in place as a best-effort – it may still work sometimes – but is no longer the thing anything depends on.

## Resolved: Cowork dashboard persistence and the Project-files-vs-local-folder distinction

Previously flagged here as unverified: whether a Cowork-produced dashboard actually becomes a persistent, pinned Artifact. Confirmed via real human-driven Cowork sessions (see `TESTING.md`): Cowork's dashboards *can* be pinned to the Artifacts library and persist across sessions, but they are **not** self-refreshing "Live Artifacts" in the sense Anthropic's connector-backed Artifacts (Slack, Gmail, calendar) are – genuine auto-refresh requires a connector called live from the browser, and this skill's data is local markdown files with no connector behind it. In practice: a pinned, persisted snapshot, pushed forward each time the dashboard is regenerated.

A second finding from the same testing, confirmed directly from Cowork's own explanation: **a Claude.ai Project's own files are read-only to Cowork, the same as they are in Chat mode** – there is no tool available to write back into a Project's knowledge from Cowork at all. A local folder is required for the tracked pipeline data to actually persist; Project files can only ever supply readable reference material (CV, JDs, cover letters) alongside it. `SKILL.md` and `README.md` have been corrected to state this plainly rather than presenting "Project files or a local folder" as two equivalent Cowork data-source choices.
