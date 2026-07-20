# Open issues

Known gaps to revisit.

None currently open.

## Resolved: Cowork dashboard persistence, corrected from an overstated claim

Previously flagged here as unverified: whether a Cowork-produced dashboard actually becomes a persistent, pinned Artifact. Now confirmed via a real human-driven Cowork session (see `TESTING.md`), with one correction to what was previously assumed: Cowork's dashboards *can* be pinned to the Artifacts library and persist across sessions, but they are **not** self-refreshing "Live Artifacts" in the sense Anthropic's connector-backed Artifacts (Slack, Gmail, calendar) are – genuine auto-refresh requires a connector called live from the browser, and this skill's data is local markdown files with no connector behind it. In practice: a pinned, persisted snapshot, pushed forward each time the dashboard is regenerated – not something that updates itself unprompted. `SKILL.md` and `README.md` have been corrected to describe this precisely rather than as "auto-updating" or "always-current," and `SKILL.md` now instructs offering to pin the dashboard as a standard part of the first regeneration in a Cowork chat, rather than requiring the user to think to ask for it separately (confirmed live: without that offer, nothing gets pinned at all).
