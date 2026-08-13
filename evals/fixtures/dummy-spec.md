# Spec: Dummy Feature (fixture)

## Objective
Fixture spec for skill evals.

## Commands
```bash
make check
```

## Project Structure
```
src/ tests/ skills/ evals/
```

## Code Style
Follow AGENTS.md.

## Testing Strategy
pytest under tests/.

## Boundaries
- Always: make check before done
- Ask first: new dependencies
- Never: commit secrets

## Success Criteria
- [ ] Eval runner passes
- [ ] Skills directory complete

## Open Questions
- None for fixture
