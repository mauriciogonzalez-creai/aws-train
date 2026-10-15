# openspec

This project uses the **OpenSpec philosophy** (proposal/design/tasks per
change, post-merge archival, traceability by Jira key) but NOT the `openspec`
CLI and NOT canonical capability specs. A change is a plain folder under
`openspec/changes/<slug>/`. When its PR merges, `/axis-archive` moves the
whole folder to `openspec/specs/<slug>/` as an append-only historical record.
`openspec/specs/` is NOT a set of living capability specs with
ADDED/MODIFIED/REMOVED deltas — do not write those here.
