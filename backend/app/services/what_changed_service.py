"""What changed — before RE:WORK vs current state."""

from app.domain.case import CaseSnapshot, WhatChangedItem, WhatChangedReport
from app.domain.enums import SourceMode


class WhatChangedService:
    def compare(
        self,
        case_id: str,
        baseline: CaseSnapshot | None,
        current: CaseSnapshot,
    ) -> WhatChangedReport:
        changes: list[WhatChangedItem] = []
        if not baseline:
            return WhatChangedReport(case_id=case_id, changes=changes)

        b = baseline.state
        c = current.state

        # Power BI capability
        b_caps = {x.get("skill_id"): x for x in b.get("candidate_capabilities", [])}
        c_caps = {
            x.get("skill_id"): x
            for x in c.get("updated_candidate_capabilities", c.get("candidate_capabilities", []))
        }
        if "power_bi" in b_caps or "power_bi" in c_caps:
            bv = b_caps.get("power_bi", {}).get("verification_status", "UNKNOWN")
            cv = c_caps.get("power_bi", {}).get("verification_status", "UNKNOWN")
            if str(bv) != str(cv):
                changes.append(
                    WhatChangedItem(
                        dimension="Power BI verification",
                        before=str(bv),
                        after=str(cv),
                        evidence_refs=c_caps.get("power_bi", {}).get("evidence_refs", []),
                    )
                )
            bp = b_caps.get("power_bi", {}).get("proficiency")
            cp = c_caps.get("power_bi", {}).get("proficiency")
            if bp is not None and cp is not None and bp != cp:
                changes.append(
                    WhatChangedItem(
                        dimension="Power BI proficiency",
                        before=f"{bp:.2f}",
                        after=f"{cp:.2f}",
                    )
                )

        # Viability
        b_v = next(
            (v for v in b.get("opportunity_viability", []) if v.get("opportunity_id") == "opp-data-analyst"),
            None,
        )
        c_v = next(
            (v for v in c.get("opportunity_viability", []) if v.get("opportunity_id") == "opp-data-analyst"),
            None,
        )
        if b_v and c_v:
            bs = b_v.get("viability_state")
            cs = c_v.get("viability_state")
            if bs != cs:
                changes.append(
                    WhatChangedItem(
                        dimension="Data Analyst viability",
                        before=str(bs),
                        after=str(cs),
                    )
                )

        # Gaps
        b_gaps = [g.get("skill_id") for g in b.get("capability_gaps", []) if g.get("gap_status") == "GENUINE_CAPABILITY_GAP"]
        c_gaps = [g.get("skill_id") for g in c.get("capability_gaps", []) if g.get("gap_status") == "GENUINE_CAPABILITY_GAP"]
        if b_gaps != c_gaps:
            changes.append(
                WhatChangedItem(
                    dimension="Genuine capability gaps",
                    before=", ".join(b_gaps) or "none",
                    after=", ".join(c_gaps) or "none",
                )
            )

        return WhatChangedReport(
            case_id=case_id,
            changes=changes,
            source_mode=SourceMode.SYNTHETIC,
        )
