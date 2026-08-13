# Task List: AI SDLC Skills Registry (generic)

Spec: [specs/ai-sdlc-skills-registry.md](../specs/ai-sdlc-skills-registry.md)  
Plan: [plan.md](plan.md)  
Guide: [README.md](../README.md)

## Phase 1: Factory foundation

- [x] Task 1: Registry + templates
- [x] Task 2: `jira-phase-gate`
- [x] Task 3: Six phase skills + `sdlc-loop`
- [x] Task 4: `.cursor/skills` symlinks
- [x] Task 5: Rubrics + evals + `make eval-skills`
- [x] Task 6: Cleanup — feature-agnostic skills; `docs/ai-sdlc/README.md`; Merge → `docs/examples/merge/`

## Checkpoint: Factory

- [x] `make eval-skills` passes
- [x] Skills do not hardcode a demo feature
- [ ] Human approves live run

## Phase 2: Live ticket (any feature)

- [ ] Task 7: MCP + choose BLRID issue key
  - Acceptance: agent can read/write issue
  - Verify: comment or label round-trip
- [ ] Task 8: `sdlc-loop` through PLAN GATE
  - Acceptance: idea/spec/plan artifacts from **ticket**; `sdlc:ideate|spec|plan` accumulated
  - Verify: outer-loop PLAN GATE presented
- [ ] Task 9: Supervised build → test → checker → VERDICT
  - Acceptance: work matches approved plan; maker ≠ checker; `sdlc:done` on ship
  - Verify: label fingerprint + evidence comments

## Phase 3: Optional follow-ups

- [ ] Task 10: Jira taxonomy doc (Outcome/Epic/Story/Bug/Spike + Component/Label/Fix/Target Version)
- [ ] Task 11: Stronger evals + sample `evals/feedback/`
- [ ] Task 12: Deploy phase decision (skill vs explicit N/A)
