---
name: idea-refine
description: >-
  Refines a Jira ticket into a sharp one-pager (inner-loop requirements). Use
  under sdlc-loop or when ideating before a spec. Feature-agnostic; grounds in
  the issue; flags duplicates and already-covered behavior. Accumulates
  sdlc:ideate. Escalates only on failure.
---

# Idea Refine (inner loop)

Adapted from [idea-refine](https://github.com/addyosmani/agent-skills/blob/main/skills/idea-refine/SKILL.md).
Orchestrated by `sdlc-loop`. See `docs/ai-sdlc/README.md`.

**Label:** `sdlc:ideate` - **Rubric:** `evals/rubrics/ideate.md`

## Deterministic

- [ ] Read the Jira issue (summary, description, AC)
- [ ] **Duplicate check** -- search same Jira project for similar open/recent issues; if found, highlight keys + overlap in the one-pager and a Jira comment
- [ ] **Already covered** -- scan repo for existing behavior that fully/partially satisfies the ticket; call it out (do not invent new scope)
- [ ] How Might We + user + success criteria
- [ ] Direction + assumptions + MVP + Not Doing
- [ ] Artifact path: `agent_space/<ISSUE-KEY>/ideas/[slug].md` (create dirs as needed)

## Reasoning

Divergent -> convergent -> one-pager. If the ticket targets this repo's product, ground in `AGENTS.md` and existing code -- without inventing scope beyond the ticket. Prefer narrowing MVP when coverage already exists.

## Intervention

Escalate only per `Skills/_templates/dual-layer.md`. No routine pause.

## What You Are NOT

- You are NOT the Spec Writer -- produce a one-pager, not a full spec
- You are NOT the Developer -- don't write code or suggest implementation
- You are NOT the PM -- don't change requirements, just clarify them
- You are NOT allowed to modify source code

## Jira

On rubric pass -> `jira-phase-gate` + `sdlc:ideate`.
(`aiagent-ready` / In Progress happen only after ideate+spec+plan via harness.)
