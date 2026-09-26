from pathlib import Path

from .profiler import load_cases
from .scout import load_cases as load_scout_cases


def main() -> None:
    profiler_cases = load_cases(Path(__file__).parents[1] / "cases" / "profiler")
    analyst_cases = load_cases(Path(__file__).parents[1] / "cases" / "analyst")
    matcher_cases = load_cases(Path(__file__).parents[1] / "cases" / "matcher")
    strategist_cases = load_cases(Path(__file__).parents[1] / "cases" / "strategist")
    scout_cases = load_scout_cases(Path(__file__).parents[1] / "cases" / "scout")
    print(
        f"Loaded {len(profiler_cases)} Profiler, {len(analyst_cases)} Analyst, "
        f"{len(matcher_cases)} Matcher, {len(strategist_cases)} Strategist, and "
        f"{len(scout_cases)} Scout evaluation cases."
    )

if __name__ == "__main__":
    main()
