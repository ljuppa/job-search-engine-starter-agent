"""Transparent arithmetic for career-value scoring."""

from .contracts import StrategistDraft


def calculate_career_score(draft: StrategistDraft) -> int:
    return max(0, min(100, 50 + len(draft.opportunities) * 12 - len(draft.risks) * 14 - len(draft.uncertainties) * 5))
