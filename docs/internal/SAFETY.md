# Safety & Security Policy for XANDER Operator

## Goals

- Protect user data and systems from accidental or malicious actions
- Ensure human control over high-impact operations
- Provide clear audit trail
- Comply with OpenClaw red lines: no exfiltration, no destructive commands without ask, trash > rm

## Risk Tiers

| Risk Level | Actions | Approval Required? | Rate Limit? |
|------------|---------|-------------------|-------------|
| HIGH | Form submit, navigation away, download, delete file, pay/transfer, credential use | Yes (explicit /approve) | Yes (per minute) |
| MEDIUM | Code execution (sandboxed), write to non-critical files, send message | No by default (can be overridden) | Optional |
| LOW | Browse, extract, screenshot, read-only clicks, compile | No | No |

See `RISK_LEVELS` in TASK_QUEUE_SPEC.md.

## Approval Mechanism

1. **Pre-action Gate**
   - Before any HIGH-risk action, orchestrator pauses.
   - Sends user message with clear details:
     - Task ID
     - What will happen
     - URL/selector involved
     - Data that will be submitted (if any)
   - Waits for `/approve <task_id>` or `/deny <task_id>`.

2. **Timeout**
   - Approval request times out after configurable period (default 10 minutes).
   - On timeout: task becomes `blocked` with reason "no approval".

3. **One-time Approval**
   - Each HIGH action requires fresh approval, even if retrying.
   - No blanket approvals.

## Secrets Management

- **Never** store credentials in task files or code.
- Use environment variables or a secrets manager (future).
- For forms that need credentials:
  - Ask user to provide at runtime via secure prompt (not logged).
  - Or use operator-level stored secrets encrypted (future: OpenClaw vault integration).

Example safe pattern:
```python
password = os.getenv("TARGET_SITE_PASSWORD")  # set externally, not in task
```

## Logging & Audit

- Daily logs in `memory/YYYY-MM-DD.md` (human-readable).
- Append-only `task_log.jsonl` for machine audit (timestamp, op, diff).
- All external requests logged: URL, method, status code.
- All approvals/denials logged with user command.

## Input Validation

- URLs: must be http/https; optionally whitelist domains.
- Selectors: basic sanity check (no newlines, reasonable length).
- Values: limit length to prevent memory exhaustion.

## Resource Limits

- Browser: max 2 concurrent instances (future pooling)
- Task queue: max 1000 entries (older ones auto-archive)
- Page content: truncate to 1MB to avoid OOM

## Incident Response

If something goes wrong:
1. Orchestrator catches exception, marks task `failed`, logs error.
2. Notifies user with `last_error` summary.
3. Does NOT auto-retry HIGH-risk failed actions without explicit request.

## Development Rules

- Code must include docstrings and type hints for safety-critical functions.
- All external dependencies pinned (requirements.txt).
- No hard-coded URLs, credentials, or tokens.
- Tests for: task manager CRUD, approval flow, error handling.

## Privacy

- No data exfiltration to third parties unless explicitly requested by user (e.g., send email).
- Scraped data stored only in task result and daily log; can be deleted on request.
- Personal information in task values should be minimal; if needed, redact in logs (MASK_SENSITIVE env var).

---

Compliance with DNA:
- TRUTH-FIRST: logs provide truth.
- RESEARCH BEFORE ACTION: approval gate ensures review.
- DOCUMENT EVERYTHING: logs + task_log.
- NO ASSUMPTIONS: approvals, validation.
- CONTEXT AWARENESS: tasks carry context.
