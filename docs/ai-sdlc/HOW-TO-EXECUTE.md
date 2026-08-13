# How to execute the AI SDLC loop

Copy-friendly runbook. Keep this open while you connect Jira and trigger the factory.

**Factory overview:** [README.md](README.md) · **Loop design:** [../design/ai-sdlc-loop.md](../design/ai-sdlc-loop.md) · **Skills:** [../../skills/REGISTRY.md](../../skills/REGISTRY.md)

---

## Prerequisites

- [ ] Cursor open on the MiniGit repo
- [ ] Skills visible under `.cursor/skills/` (symlinks to `skills/`)
- [ ] Atlassian account with access to project **BLRID**
- [ ] `gh` authenticated for PRs (branch pattern `aiagent/<ISSUE-KEY>`)
- [ ] Jira API token (or OAuth) ready — **do not commit tokens; do not paste them into chat**

Smoke-test the registry anytime:

```bash
make eval-skills
```

---

## Step 1 — Connect Jira (Atlassian MCP)

Credentials go in **your user Cursor config**, not in this git repo:

**File:** `~/.cursor/mcp.json`

### Option A — API token (Basic auth)

Encode locally (do not share the output in tickets/chat):

```bash
echo -n "YOUR_EMAIL:YOUR_API_TOKEN" | base64 -w0
echo
```

Add (merge with any existing `mcpServers` entries such as `weather`):

```json
{
  "mcpServers": {
    "atlassian": {
      "url": "https://mcp.atlassian.com/v1/mcp",
      "headers": {
        "Authorization": "Basic PASTE_BASE64_HERE"
      }
    }
  }
}
```

Docs: [Configuring authentication via API token](https://support.atlassian.com/atlassian-rovo-mcp-server/docs/configuring-authentication-via-api-token/)

### Option B — OAuth (browser)

```json
{
  "mcpServers": {
    "atlassian": {
      "url": "https://mcp.atlassian.com/v1/mcp/authv2"
    }
  }
}
```

Complete the browser sign-in when Cursor prompts.

### After saving

1. Restart Cursor **or** Settings → MCP → toggle Atlassian off/on.
2. Confirm the server is **connected** (not error / needsAuth).
3. Optional check: ask the agent *“List or get BLRID issue … using Atlassian MCP”*.

---

## Step 2 — Create or pick a trigger ticket

1. Open [BLRID board].
2. Create (or choose) an issue for **any** feature/work item.
3. Fill summary + description / acceptance criteria (agents derive scope from this).
4. Copy the issue key, e.g. `BLRID-123`.

You do **not** need labels beforehand; the loop adds them as phases pass. If labels already exist, the loop **resumes** at the next phase.

**Progress labels:**  
`sdlc:ideate` → `sdlc:spec` → `sdlc:plan` → `sdlc:implement` → `sdlc:test` → `sdlc:review` → `sdlc:done`  
(plus `sdlc:blocked` on escalate)

**Gate labels you will use:**

| Label | Who sets | Meaning |
|-------|----------|---------|
| `sdlc:agent-ready` | Agent (after ideate+spec+plan) | Ready for human plan review; **Jira comment** with idea/spec/tasks (Description left intact); status → **In Progress** |
| `sdlc:human-ready` | **You** (or comment `approved`) | Unblock maker / acknowledge gate |
| `sdlc:agent-approved` | Agent (after PR opened) | Implementation ready for your PR review |
| `sdlc:need-review-stage` | **You** | Ask agent to incorporate review feedback (agent clears stale `sdlc:human-ready` / `sdlc:agent-approved` for you) |

---

## Step 3 — Trigger the loop in Cursor

Paste (edit the key):

```text
Use the sdlc-loop skill on BLRID-123 in supervised mode.

- Resume from existing `sdlc:*` labels (do not restart finished phases).
- Read the Jira issue as the only source of feature scope.
- Flag duplicate tickets and already-covered code early.
- After ideate+spec+plan: sdlc:agent-ready + status In Progress; stop for HUMAN GATE.
- Implement only when sdlc:agent-ready and sdlc:human-ready are present.
- PR branch: aiagent/BLRID-123; set sdlc:agent-approved when ready.
- After I approve the PR: status Review; checker adds inline comments.
- If I add sdlc:need-review-stage, incorporate that feedback.
- Stop for me on: HUMAN GATE, ESCALATE, VERDICT, or missing gates.
```

Optional teaching mode (you approve every phase):

```text
Same as above, but autonomy=interactive (pause after each phase).
```

---

## Step 4 — What you do on the outer loop

| Packet | When | Your action |
|--------|------|-------------|
| **HUMAN GATE (plan)** | After `sdlc:agent-ready` | Add `sdlc:human-ready` **or** comment `approved` / change X / `stop` |
| **HUMAN GATE (PR)** | After `sdlc:agent-approved` + PR | Review PR; approve → agent moves status to **Review** |
| **Feedback** | Anytime in review | Add `sdlc:need-review-stage` + comments; re-run loop. **You do not remove** `sdlc:human-ready` — the agent does. Re-approve when satisfied. |
| **ESCALATE** | Failure, ask-first, Critical, MCP down | redirect / fix constraint / abort |
| **VERDICT** | After checker review | `ship` / `block` / `redirect` / `narrow` |

On **ship**, the harness accumulates `sdlc:done`.

---

## Step 5 — Verify it worked

On the Jira issue, confirm:

- [ ] Evidence **comments** for completed phases
- [ ] Accumulated **`sdlc:*`** and gate labels
- [ ] Status moved to **In Progress** at ready gate; **Review** after PR approval (if workflow allows)
- [ ] PR on branch `aiagent/<KEY>`
- [ ] Repo artifacts under `agent_space/<KEY>/` (ideas, specs, tasks, reviews) — not under product `docs/`
- [ ] Product code/tests only if the ticket required them (`src/`, `tests/`)

Local registry still healthy:

```bash
make eval-skills
```

If the ticket changed MiniGit code:

```bash
make check
```

---

## Troubleshooting

| Symptom | What to do |
|---------|------------|
| Agent says no Atlassian/Jira tools | Fix `~/.cursor/mcp.json`; restart/toggle MCP; confirm auth |
| Agent restarts from ideate | Remind: resume from labels |
| Maker starts without approval | Remind: need `sdlc:agent-ready` + `sdlc:human-ready` |
| Labels not applied | Check MCP write permission; use `jira-phase-gate` after rubric pass |
| Status not Review | Workflow may lack Review; check agent comment for alias miss |
| Agent invents a feature | Remind: scope = this issue only |
| Skills not found | `ls -la .cursor/skills/`; should symlink to `../../skills/...` |

---

## One-page cheat sheet

```text
1. ~/.cursor/mcp.json → Atlassian MCP connected
2. BLRID-XXX ticket with clear AC
3. Cursor: “Use sdlc-loop on BLRID-XXX (supervised)”
4. You: sdlc:human-ready after sdlc:agent-ready → review PR → optional sdlc:need-review-stage → VERDICT
5. Check Jira labels/status + PR aiagent/BLRID-XXX
```

Optional sample feature narrative (not required to run): [docs/examples/merge/](../examples/merge/).
