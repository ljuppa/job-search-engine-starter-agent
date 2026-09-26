from pathlib import Path

from .profiler import load_cases


def main() -> None:
    profiler_cases = load_cases(Path(__file__).parents[1] / "cases" / "profiler")
    analyst_cases = load_cases(Path(__file__).parents[1] / "cases" / "analyst")
    matcher_cases = load_cases(Path(__file__).parents[1] / "cases" / "matcher")
    print(f"Loaded {len(profiler_cases)} Profiler, {len(analyst_cases)} Analyst, and {len(matcher_cases)} Matcher evaluation cases.")

if __name__ == "__main__":
    main()
