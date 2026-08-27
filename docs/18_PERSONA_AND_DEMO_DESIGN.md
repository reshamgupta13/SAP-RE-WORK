# 18 — Persona and Demo Design

**Strategy:** one exceptional end-to-end scenario. Engine remains persona-agnostic.

Persona-specific logic lives in **fixtures and content**, not `if gender ==` or `if city == Lucknow` in the scorer.

---

## 1. Flagship persona — Ananya Sharma (demo name)

| | |
|---|---|
| Age | 28 |
| Location | Lucknow, Uttar Pradesh |
| Situation | Returning after **3-year caregiving break** |
| Before break | Business Analyst / MIS in a shared-services / ops-analytics setting (India) |
| Capabilities evidenced | Requirements gathering, stakeholder communication, Excel (advanced), SQL (working–independent), process documentation, Hindi + English |
| Stale / weak | Power BI / Looker-style dashboards; cloud data warehouses; “current” commercial tenure |
| Constraints volunteered | Cannot relocate immediately; hybrid/remote preferred; weekday daytime hours |
| Target | Junior Data Analyst / BI Analyst (India, hybrid-capable) |
| Non-goal | Do not award points for being a woman. The story is **capability + proxies + one gap**. |

**Traditional ATS outcome (scripted foil):**  
Does not meet: 3 years continuous experience; Bangalore location; premier institute preferred; recent relevant employment.

**RE:WORK outcome:**  
Strong demonstrated capability on core tasks. Mismatch is primarily career-history and location **proxies**, plus one **trainable** visualization gap. Pathway ~4 weeks + SQL/BI proof. Readiness: `ready_with_bounded_pathway`. HR decides on location policy.

---

## 2. Reusable engine — other personas as fixtures, same graph

| Persona type | What changes | What must not be hardcoded |
|---|---|---|
| Career returner | Timeline break, recency | Gender |
| Displaced worker | Last title sunset, adjacent skills | “pity match” |
| Rural / tier-2/3 | Location, institute, language | Prestige boost inverse |
| Disability / accessibility | **Volunteered** constraints vs job conditions | Inference from text |
| Credential proxy victim | Strong artifacts, weak brand | Auto-drop degrees |
| Experience proxy | Strong tasks, few years | Auto-drop years |
| Genuine skill gap | Missing core capability | Calling it a proxy |
| Mixed | Both gap and proxy | Collapsing to one score |
| Highly qualified | ready_now | Over-pathwaying |
| Underqualified | not_ready honest | Inflated readiness |
| Adjacent skills | transfer edges | Claiming explicit mastery |
| Internal mobility | SAP context filled | Different matcher |
| Reskilling | longer path / no_viable_path | Fake 1-week data-science path |

Each is a `demo_scenario_id` with JSON fixtures. Same orchestrator.

---

## 3. Demo data pack (to build after approval)

- `candidates/ananya.json` + resume text
- `jobs/junior_data_analyst_noisy.json` (proxies in JD)
- `jobs/junior_data_analyst_clean.json` (optional contrast)
- `sap/growth_portfolio_ananya.simulated.json`
- `opportunities/*.json` (~15–25)
- `market_signals.synthetic.json`
- `proof/sql_mini_pass.json` (demo lock)
- `golden/ananya_run.json` expected artifacts for eval

All files carry `provenance`.

---

## 4. What “not hardcoded” means in code review

Forbidden:

```
if candidate.city == "Lucknow": score += 10
if "caregiving" in resume: diversity_boost()
```

Allowed:

```
constraints.work_modes  # from profile
requirement.class == "D_experience"
```

---

## 5. Live end-to-end demo shape

Single run_id, visible in Control Room, both Candidate and HR views bound to the same objects. See `19_DEMO_SCRIPT.md`.
