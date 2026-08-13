# Rubric: review

## Pass if

- [ ] Five-axis review produced
- [ ] Severity labels used
- [ ] Checker pass separate from maker
- [ ] Inline comments for unvalidated logic, missing AC coverage, edge cases
- [ ] `aiagent-need-review-stage` feedback addressed or explicitly tracked
- [ ] Critical/Required issues resolved or deferred with justification

## Fail if

- LGTM without evidence
- Security issues ignored (SQL, secrets, hash/ref validation)
- Skipped inline findings when tests/AC gaps are obvious
