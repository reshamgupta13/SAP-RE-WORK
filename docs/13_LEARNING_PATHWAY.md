# 13 — Learning Pathway

Learning is valid only when bound to:

**TARGET ROLE + CAPABILITY GAP + PROOF OF SKILL**

Not: “Here are 10 random courses.”

---

## 1. Pathway object

```json
{
  "path_id": "uuid",
  "target_role_id": "junior_data_analyst",
  "policy": {"max_weeks": 6, "hours_per_week": 8},
  "items": [
    {
      "id": "i1",
      "target_skill_id": "power_bi",
      "why_it_matters": "Core tasks include recurring visual reports for ops leadership.",
      "starting_proficiency": 0.22,
      "target_proficiency": 0.60,
      "learning_items": [
        {
          "title": "TBD — map to SAP Learning Hub title if verified",
          "sap_learning_item_id": null,
          "source": "synthetic_catalog",
          "provenance": "SYNTHETIC",
          "hours": 8
        }
      ],
      "practical_exercise": "Rebuild last-week KPI pack from sample CSV",
      "proof_of_skill_id": "bi_dashboard_mini",
      "expected_duration_weeks": 2,
      "confidence": 0.7,
      "progress": 0.0,
      "completion_criteria": "proof pass + exercise submitted"
    }
  ],
  "total_weeks": 4,
  "status": "proposed|accepted|in_progress|completed|rejected",
  "no_viable_path": false
}
```

---

## 2. Construction rules

1. Only skills in `gaps` with `type=capability` and `severity=trainable` (or evidence-stale currency).
2. Do not add prestige MOOCs that do not map to a gap.
3. Hours/weeks from a **static table** (skill × delta proficiency), not from the LLM.
4. Each blocking gap has a proof task.
5. If total_weeks > policy.max_weeks → `no_viable_path` or split “phase 1 unlocks intern/analyst contract” as an *alternative role*, not a fake short path.
6. Mentorship is a **learning item type** (`mentorship`) with no fake named mentors in demo unless labeled SYNTHETIC.

---

## 3. SAP Learning mapping

| Situation | Behavior |
|---|---|
| SuccessFactors Learning API **[NOT VERIFIED]** | Do not call. Store `sap_learning_item_id=null` |
| Team provides real Learning Hub course titles | Put titles in catalog with provenance `USER-PROVIDED` or `LIVE` if copied from their hub |
| Practice LMS live | Map IDs; assignment write-back **human-approved only**, P2 |

Never display a generated “SAP course ID.”

---

## 4. Progress

P0: manual/demo progress flags.  
P1: tick exercises + proof.  
Completion of a video without proof cannot set proficiency to target.

---

## 5. Candidate vs HR

- Candidate sees time, why, proof.
- HR sees which gaps the path is meant to close and which proxies it does **not** waive until they say so.

Pathway acceptance is a human decision (`learning_path.status=accepted`) before we talk as if the person is “in a program.”
