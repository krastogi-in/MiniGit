# Plan: MiniGit status (BLRID-11)

PR branch when implement starts: `aiagent/BLRID-11`

## Architecture

```
CLI / Flask → Operations.status() → HEAD ref + get_staged()
                 ↑
         checkout updates HEAD
```

## Tasks

| # | Task | Size | Kind |
|---|------|------|------|
| 1 | Persist/read HEAD for current branch (init already sets HEAD; checkout writes HEAD; Operations loads HEAD) | M | build (gap fix) |
| 2 | `Operations.status()` returning branch + staged list | S | build (reuse get_staged) |
| 3 | TDD tests for status AC | M | build |
| 4 | CLI `minigit status` | S | build |
| 5 | Flask status UI | S | build |
| 6 | AC close-out + `make check` + open PR | S | verify |

## Checkpoints

- After tasks 1–2: status API works in REPL/tests with correct branch across new Operations()
- After tasks 3–4: CLI green under pytest
- After 5–6: Flask wired; PR on `aiagent/BLRID-11`

## Notes

- No feature code in this phase.
- Working-dir page already shows staged for staging UX — status UI may be a dedicated section/route summarizing branch + staged (ticket AC).
