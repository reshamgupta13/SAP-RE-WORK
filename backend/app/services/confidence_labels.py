"""Map numeric confidence to explicit labels — not statistical calibration."""

from app.domain.enums import ConfidenceLabel


def to_confidence_label(score: float) -> ConfidenceLabel:
    if score >= 0.75:
        return ConfidenceLabel.HIGH_CONFIDENCE
    if score >= 0.55:
        return ConfidenceLabel.MEDIUM_CONFIDENCE
    if score >= 0.35:
        return ConfidenceLabel.LOW_CONFIDENCE
    return ConfidenceLabel.UNCERTAIN


def confidence_label_text(label: ConfidenceLabel) -> str:
    mapping = {
        ConfidenceLabel.HIGH_CONFIDENCE: "High confidence based on available evidence.",
        ConfidenceLabel.MEDIUM_CONFIDENCE: "Moderate confidence — some evidence gaps remain.",
        ConfidenceLabel.LOW_CONFIDENCE: "Low confidence — limited supporting evidence.",
        ConfidenceLabel.UNCERTAIN: "Uncertain — insufficient evidence for a reliable projection.",
    }
    return mapping.get(label, mapping[ConfidenceLabel.UNCERTAIN])
