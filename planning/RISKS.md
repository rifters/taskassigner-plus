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
| UI shell regressions break existing role flows | Medium | High | Keep backend contracts stable; add route-level smoke tests across manager/crew/owner before/after UI wiring. | Active |
| Pilot host PC unavailable | Current | High | Complete local hardening and rehearsal now; maintain a host-PC follow-up checklist and do not approve live pilot access until host checks pass. | Accepted/deferred |
| Schedule PDF structure may vary | Medium | Medium | Keep the initial schedule phase limited to day-level work detection with manual review; do not build time/analytics features until structured export is confirmed. | Accepted/deferred |
|| Mobile readability too poor for crew usage | Medium | High | Mobile-first crew page constraints (single-column, large tap targets, concise status states) + manual viewport checks. | Active |
| Per-person exclusions become stale after task deletion | Low | Medium | Foreign keys, normalized exclusion rows, and deletion-order cleanup; retain stable task-template identity rather than title strings. | Mitigated |
