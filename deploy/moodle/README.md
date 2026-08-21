# Moodle Integration Boundary

Moodle is an independent training system. The product hub stores only the
course association and launch metadata; it does not copy credentials or
implement a second examination engine. The deployment contract is:

- Moodle 4.5 LTS in an isolated stack and database.
- Hub integration through a configured base URL and signed launch/token flow.
- `TRAINING_VIEW` controls visibility; `TRAINING_ADMIN` controls association
  management.
- Health and launch verification are required before Gate C can pass.

The formal server currently has no Moodle image or installation source, so this
boundary remains un-deployed until a reachable image source is available.
