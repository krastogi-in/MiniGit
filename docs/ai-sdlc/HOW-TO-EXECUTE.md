# How to execute the AI SDLC loop

Copy-friendly runbook. Keep this open while you connect Jira and trigger the factory.

**Factory overview:** [README.md](README.md) · **Loop design:** [../design/ai-sdlc-loop.md](../design/ai-sdlc-loop.md) · **Skills:** [../../Skills/REGISTRY.md](../../Skills/REGISTRY.md)

---

## Prerequisites

- [ ] Cursor open on the MiniGit repo
- [ ] Skills visible under `.cursor/skills/` (symlinks to `Skills/`)
- [ ] Atlassian account with access to project **BLRID**
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
echo -n "YOUR_EMAIL@redhat.com:YOUR_API_TOKEN" | base64 -w0
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

1. Open [BLRID board](https://redhat.atlassian.net/jira/software/c/projects/BLRID/issues).
2. Create (or choose) an issue for **any** feature/work item.
3. Fill summary + description / acceptance criteria (agents derive scope from this).
4. Copy the issue key, e.g. `BLRID-123`.

You do **not** need `sdlc:*` labels beforehand; the loop adds them as phases pass.

**Suggested labels the factory will accumulate:**  
`sdlc:ideate` → `sdlc:spec` → `sdlc:plan` → `sdlc:implement` → `sdlc:test` → `sdlc:review` → `sdlc:done`  
(plus `sdlc:blocked` on escalate)

---

## Step 3 — Trigger the loop in Cursor

Paste (edit the key):

```text
Use the sdlc-loop skill on BLRID-123 in supervised mode.

- Read the Jira issue as the only source of feature scope.
- Run the AI SDLC inner loop (idea → spec → plan → implement → test → review).
- Update BLRID via jira-phase-gate after each rubric pass (accumulate sdlc:* labels; do not remove prior ones).
- Stop for me only on: PLAN GATE, ESCALATE, or VERDICT.
- Maker and checker must be separate passes.
```

Optional teaching mode (you approve every phase):

```text
Same as above, but autonomy=interactive (pause after each phase).
```

---

## Step 4 — What you do on the outer loop

| Packet | When | Your action |
|--------|------|-------------|
| **PLAN GATE** | After plan/todo exist | `yes` / change X / `stop` |
| **ESCALATE** | Failure, ask-first, Critical, MCP down | redirect / fix constraint / abort |
| **VERDICT** | After checker review | `ship` / `block` / `redirect` / `narrow` |

You should **not** be asked “should I do the next implement task?” in supervised mode.

On **ship**, the harness accumulates `sdlc:done`.

---

## Step 5 — Verify it worked

On the Jira issue, confirm:

- [ ] Evidence **comments** for completed phases
- [ ] Accumulated **`sdlc:*` labels** (fingerprint of progress)
- [ ] Repo artifacts as appropriate (`docs/ideas/`, `docs/specs/`, `tasks/`, code/tests if the ticket required them)

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
| Labels not applied | Check MCP write permission on BLRID; agent must use `jira-phase-gate` only after rubric pass |
| Agent asks every step | Remind: supervised `sdlc-loop`; only PLAN / ESCALATE / VERDICT |
| Agent invents a feature | Remind: scope = this issue only; no hardcoded demo features |
| Skills not found | `ls -la .cursor/skills/`; should symlink to `../../Skills/...` |

---

## One-page cheat sheet

```text
1. ~/.cursor/mcp.json → Atlassian MCP connected
2. BLRID-XXX ticket with clear AC
3. Cursor: “Use sdlc-loop on BLRID-XXX (supervised)”
4. You: PLAN GATE → (agents work) → ESCALATE if needed → VERDICT
5. Check Jira comments + sdlc:* labels
```

Optional sample feature narrative (not required to run): [docs/examples/merge/](../examples/merge/).
