# Open issues

Known gaps to revisit.

## Cowork Live Artifact dashboard-persistence claim not yet verified end-to-end

`SKILL.md`/`README.md` now state that a Cowork-produced dashboard is a Live Artifact – pinnable, saved to the Artifacts library, auto-updating – citing Anthropic's own documentation for the platform feature itself. Not yet confirmed that this skill's own `inject_data()` → Artifact flow, run inside a genuinely fresh Cowork session, actually produces a Live Artifact rather than a plain one. Claude Code cannot test this directly – Cowork is desktop-app-only, and computer-use tooling is explicitly blocked from controlling Claude's own application. Needs a human-driven Cowork session (see the planned Cowork blind test in `TESTING.md`) with results reported back.

Separately, confirmed and already documented: a Chat-mode dashboard Artifact *can* be manually published (one click, by the user) to appear in the Artifacts library and get a shareable URL, but it's a static snapshot, not a Live Artifact – it doesn't auto-update and isn't pinnable. This was verified directly.
