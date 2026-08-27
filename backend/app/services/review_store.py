"""In-memory human review storage."""

from app.domain.decision import HumanReview


class ReviewStore:
    def __init__(self) -> None:
        self._reviews: dict[str, HumanReview] = {}
        self._by_run: dict[str, list[str]] = {}

    def save(self, review: HumanReview) -> HumanReview:
        self._reviews[review.id] = review
        self._by_run.setdefault(review.run_id, []).append(review.id)
        return review

    def get(self, review_id: str) -> HumanReview | None:
        return self._reviews.get(review_id)

    def list_for_run(self, run_id: str) -> list[HumanReview]:
        ids = self._by_run.get(run_id, [])
        return [self._reviews[i] for i in ids if i in self._reviews]


review_store = ReviewStore()
