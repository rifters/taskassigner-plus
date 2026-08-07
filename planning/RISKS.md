# Risks

Known project risks and mitigation notes.

---

| Risk | Likelihood | Impact | Mitigation | Status |
|---|---:|---:|---|---|
| PIN brute-force against crew auth | Medium | High | Lockouts, strict auth rate limits, failed-attempt auditing, alert thresholds. | Active |
| Privilege escalation / horizontal data access | Medium | High | Server-side role checks on every endpoint, per-role tests, deny-by-default authorization. | Active |
| Forged completion events | Medium | High | Ownership checks, immutable audit records, manager confirmation state, tamper-resistant logs. | Active |
| Public tunnel attack surface | Medium | High | HTTPS only, secure cookie/session settings, CSRF defense, input validation, dependency hygiene. | Active |
| Sensitive data leakage in logs | Low | High | Structured logs with redaction policy, no secrets/PIN/password logs, restricted log access. | Active |
| Scope creep in first build sprint | High | Medium | Enforced in/out-of-scope list, acceptance gates, explicit exclusions. | Active |
| Cold-start fairness quality in week one | Medium | Medium | Mark first-cycle caveat in UI/reporting, allow manager override with audit trail. | Accepted |
| Operational fragility (backup/alerts absent) | Medium | High | Daily backups, restore verification steps, uptime/error alerts to manager. | Active |
| Manager override misuse (false completions) | Medium | High | Mandatory reason + actor attribution + reporting distinction between self and on-behalf completion. | Active |
| Notes abuse/noise or accidental sensitive content | Medium | Medium | Short note length cap, input sanitization, write-once immutability, manager-visible context. | Active |
