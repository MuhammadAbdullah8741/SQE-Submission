# Browser and non-functional verification

Owner: M Abdullah (24i-3050)

This package supplies browser-level evidence for all six use cases and focused non-functional checks. UC5 verifies stock allocation at the last-copy and multi-copy boundaries. UC6 verifies that the selected active loan, rather than another or stale transaction, is returned. The same Playwright suite also checks the four authorization decisions: librarian issue/return allowed and student issue/return denied.

## Evidence covered

- `workflows.spec.cjs`: 33 browser tests covering UC1-UC6, keyboard operation, session-cookie flags, and the two-role access matrix.
- `../evidence/playwright-results.json`: 33 passed, zero failed, zero skipped.
- `../evidence/axe-before.json` and `axe-after.json`: accessibility regression evidence, from four violations to zero.
- `../evidence/lighthouse-*-before.json` and `lighthouse-*-after.json`: issue and return accessibility scores improved from 0.85 to 1.00.
- `../evidence/k6-run-status.json`: two 1-VU and two 5-VU performance runs, all successful.

## Reproduce the evidence integrity check

From the repository root, run:

```powershell
python tests/team/scripts/check_nonfunctional_evidence.py
```

The command exits non-zero if a required use case, authorization scenario, successful load run, passing browser result, or final accessibility result is missing.
