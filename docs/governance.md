# Security and governance demonstration
Only synthetic student information is included.

- Local `masked_students` SQL view hides most of the email; Fabric writes `gold_masked_students`.
- This is a masking demonstration, not a security boundary: a user with base-table access can see raw email.
- Proposed column security: grant consumer access only to masked Gold objects, restrict Silver/Bronze to pipeline identities and maintainers.
- Proposed row security: expose a course-scoped view for instructors, bind authenticated instructor identity to authorized course IDs; enforce in the serving layer/SQL endpoint or semantic model. Never accept caller-supplied course ID as authorization.
- Catalog metadata is supplied in metadata_catalog.json. Apply equivalent classifications/descriptions in the target Fabric catalog.
- No credentials are required locally. `.env.example` is illustrative; real `.env` files are excluded from Git.
