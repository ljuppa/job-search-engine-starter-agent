from pathlib import Path

from .profiler import load_cases


def main() -> None:
    profiler_cases = load_cases(Path(__file__).parents[1] / "cases" / "profiler")
    analyst_cases = load_cases(Path(__file__).parents[1] / "cases" / "analyst")
    print(f"Loaded {len(profiler_cases)} Profiler and {len(analyst_cases)} Analyst evaluation cases.")

if __name__ == "__main__":
    main()
