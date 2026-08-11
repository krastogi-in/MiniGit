---
name: idea-refine
description: >-
  Refines a Jira ticket into a sharp one-pager (inner-loop requirements). Use
  under sdlc-loop or when ideating before a spec. Feature-agnostic; grounds in
  the issue. Accumulates sdlc:ideate. Escalates only on failure.
---

# Idea Refine (inner loop)

Adapted from [idea-refine](https://github.com/addyosmani/agent-skills/blob/main/skills/idea-refine/SKILL.md).  
Orchestrated by `sdlc-loop`. See `docs/ai-sdlc/README.md`.

**Label:** `sdlc:ideate` · **Rubric:** `evals/rubrics/ideate.md`

## Deterministic

- [ ] Read the Jira issue (summary, description, AC)
- [ ] How Might We + user + success criteria
- [ ] Direction + assumptions + MVP + Not Doing
- [ ] Artifact path (default `docs/ideas/[slug].md`)

## Reasoning

Divergent → convergent → one-pager. If the ticket targets this repo’s product, ground in `AGENTS.md` and existing code — without inventing scope beyond the ticket.

## Intervention

Escalate only per `Skills/_templates/dual-layer.md`. No routine pause.

## Jira

On rubric pass → `jira-phase-gate` + `sdlc:ideate`.
