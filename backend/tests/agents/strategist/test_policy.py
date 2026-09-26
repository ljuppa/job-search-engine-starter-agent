from src.agents.strategist import StrategicSignal, StrategistDraft
from src.agents.strategist.policy import calculate_career_score


def test_career_score_is_deterministic_and_penalises_uncertainty() -> None:
    draft = StrategistDraft(opportunities=[StrategicSignal(category="scope", detail="Growth", confidence=1)], uncertainties=[StrategicSignal(category="market", detail="Unknown portability", confidence=0.5)])
    assert calculate_career_score(draft) == 57
