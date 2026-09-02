"""Product catalog case execution tests."""

from app.domain.enums import CaseStage
from app.services.case_service import CaseService


def test_product_case_finale_user002():
    svc = CaseService()
    case = svc.create_case(candidate_id="USER002", job_id="JOB002", opportunity_id="JOB002")
    case = svc.execute(case.id, execute_until=CaseStage.FINALE)
    assert case.lifecycle_state.value == "EXPLANATION_READY"
    assert len(case.snapshot.get("candidate_capabilities") or []) >= 1
