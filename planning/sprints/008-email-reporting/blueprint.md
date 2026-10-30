# Blueprint

1. Extend the report payload with weekly summary metrics and assignment-level rows.
2. Resolve recipients from active `User` records with role `manager` or `owner` and valid email; retain the legacy configured recipient as a compatibility fallback.
3. Render a multipart email: HTML summary, text fallback, and CSV attachment.
4. Update scheduled, manual, and test sends to use the shared message builder and recipient list.
5. Keep existing report JSON routes and SMTP configuration behavior compatible.
