# Final Limitations

## SAP

- No verified live tenant in demo environment
- Live data reads not implemented (`NotImplementedError`)
- BTP / Integration Suite not connected
- Write-back simulated only

## AI

- DEMO_FALLBACK used when LLM unavailable
- Confidence labels are heuristic, not calibrated probabilities

## Data

- Market signals: SYNTHETIC
- Ananya proof: demo fixture (`is_demo: true`)
- Intervention results: SIMULATED PROJECTION

## Security

- No production authN/Z
- CORS: localhost only
- Credentials env-only; redacted in export

## Persistence

- Default: in-memory (lost on restart)

## Not claimed

- Guaranteed employment
- Bias removal
- Autonomous hiring
- Production-grade security
