# Acceptance Criteria

- [x] Active managers with valid email addresses receive the report.
- [x] Active owners with valid email addresses receive the report.
- [x] Inactive users, crew, shift leads, and users without valid email are excluded.
- [x] Duplicate recipient addresses are removed.
- [x] Subject and body identify the Thursday–Wednesday reporting range.
- [x] Summary includes assigned, completed, not-completed, completion rate, completion source counts, top five never-finished people, and lowest-rate rankings.
- [x] CSV attachment contains one row per posted assignment and completion metadata.
- [x] Manual, scheduled, and test sends share recipient and rendering logic.
- [x] Existing SMTP guards and report API contracts remain passing.
- [x] Full tests, compilation, and whitespace validation pass.
