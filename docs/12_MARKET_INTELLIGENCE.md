# 12 — Market Intelligence

The brief requires Market Intelligence as a **real orchestrator capability**, not a decorative dashboard.

It must answer:

- What skills are growing / declining **in our demo corpus**?
- Which roles are adjacent?
- Where is this candidate’s capability useful?
- Which **small** skill investment unlocks multiple opportunities?

---

## 1. Data honesty

| Source | Status | UI label |
|---|---|---|
| Live job-board crawl | Out of P0 (brittle, ToS, hallucination of “the market”) | — |
| Licensed labor-market API | **[NOT VERIFIED]** | — |
| SAP People Intelligence | **[NOT VERIFIED]** | — |
| Curated `market_signals` table | **[SYNTHETIC]** for prototype | Required banner: “Demo market corpus — not national statistics” |
| Derived from *our* opportunity set | **[SYNTHETIC]** or **[SIMULATED]** | “Based on N demo opportunities” |

**Never fabricate “real-world market statistics.”**  
Do not quote IDC/WEF numbers as if RE:WORK computed them. Those belong in the pitch, cited to the SAP brief, not in the product UI as live KPIs.

---

## 2. Corpus design (prototype)

Seed ~25–40 opportunities (Lucknow / hybrid / India analytics & ops) and ~30 skills.

Each `MarketSignal` row:

```json
{
  "skill_id": "power_bi",
  "window": "demo_2026q3",
  "demand_index": 0.82,
  "trend": "up|flat|down",
  "adjacent_role_ids": ["junior_data_analyst", "mis_executive"],
  "opportunity_count": 11,
  "notes": "Counted inside RE:WORK demo corpus only",
  "provenance": "SYNTHETIC"
}
```

`demand_index` is **normalized within the corpus**, not a rupee wage.

---

## 3. Questions → queries (deterministic)

| Question | Method |
|---|---|
| Growing skills | `trend=up` sort by demand_index |
| Declining | `trend=down` |
| Adjacent roles | Graph: shared core skills ≥ k with target role |
| Where is the candidate useful | Overlap of candidate independent-level skills with opportunity skill bags |
| Small investment, many doors | For each missing adjacent skill, count opportunities that would move to `ready_with_bounded_pathway` or better if that skill reached min_proficiency — pick max unlock / hour from pathway table |

LLM writes a briefing that **may only cite** `signal_id` / `opportunity_id`. If it adds a percentage not in the table, drop the prose.

---

## 4. Role in the loop

- **Pathway:** prefer learning items that unlock the most corpus opportunities (Power BI over a random certification).
- **Matching:** do not boost rank by “hot skill” if the candidate lacks it — that recreates trend-chasing bias. Use market data to **explain** why a gap is worth closing.
- **HR:** “If you keep the Power BI bar, here is the pathway; if you accept Excel+SQL proof first, three more demo roles open.”

---

## 5. UI

A small panel: top skills in corpus, adjacent roles, “unlock” recommendation with counts. Every number has a footnote: corpus size and provenance.

---

## 6. P1+ if a real feed appears

Adapter `MarketFeed` with provenance LIVE. Same queries. Until then, synthetic only.
