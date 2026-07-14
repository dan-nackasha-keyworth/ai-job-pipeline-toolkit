# Open issues

Known gaps to revisit.

## Score visibility for non-interview-stage applications

Score rationale currently only surfaces in full via the Briefing Pack, which is only generated once an application reaches `interviewing` or later. Most applications never get that far, so their score rationale lives only in the application file's own prose, with no dashboard-level way to browse or compare it. Worth deciding whether the dashboard should surface a condensed score rationale for every application, not just ones with a full Briefing Pack.

## Duplicate/reposted-role detection

The skill has no check for whether a company+role combination has already been scored or applied to before creating a new application file. Worth adding a lightweight pre-check that flags a likely duplicate or repost rather than silently creating a second record.
