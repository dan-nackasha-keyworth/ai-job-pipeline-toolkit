# Open issues

Known gaps to revisit.

## Example dataset's Score rationale text is thin

Every one of the 37 example applications' `## Score rationale` section just restates the component score (`"JD fit: 41/45"`) rather than the one-line reasoning `SKILL.md` Step 2's own "Output" instruction calls for. The dashboard now correctly surfaces this section on every card (see `TESTING.md` Test 18), but the demo content itself isn't a good showcase of that feature's value. Worth rewriting rationale text for at least a representative subset of examples with real, specific reasoning per component.

## Duplicate/reposted-role detection

The skill has no check for whether a company+role combination has already been scored or applied to before creating a new application file. Worth adding a lightweight pre-check that flags a likely duplicate or repost rather than silently creating a second record.
