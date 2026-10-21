# Historical evaluation source

[release-v1.1.4](release-v1.1.4/source.json) contains the exact public skill files and manifest used for the original evaluation. They were exported from the existing `v1.1.4` Git tag and verified against every file hash in the unchanged runtime environment before the current skill was updated.

This is an inactive evidence snapshot. The distributable plugin and installer use the top-level `skills/` directory. Historical answer records are checked against their own source, rather than silently being relabeled as evidence for changed instructions.
