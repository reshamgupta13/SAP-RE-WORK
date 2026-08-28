# Final Demo Flow

## Operator path (no typing)

1. Open `/control-room`
2. Click **WHY WAS SHE REJECTED?** — traditional vs RE:WORK
3. Review **Agent Orchestrator** — SAP → agents → engines
4. Click **WHY?** on Decision Card — evidence chain
5. Toggle **WHAT IF** interventions — projected scenarios
6. Show **SAP vs RE:WORK** panel
7. Optional: **Negative case** button (B07/B14/B20)
8. Record **Human Decision** in footer
9. **RESET CASE** if needed

## Recovery

`POST /api/demo/reset` — no server restart.

## Modes

| Mode | Behavior |
|------|----------|
| DEMO_MODE=true | SIMULATED SAP, DEMO_FALLBACK AI |
| SAP unavailable | Explicit SIMULATED label + fallback_reason |
| LLM unavailable | DEMO_FALLBACK completes case |
