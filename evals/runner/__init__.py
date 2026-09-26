from pathlib import Path

from .profiler import load_cases


def main() -> None:
    case_directory = Path(__file__).parents[1] / "cases" / "profiler"
    cases = load_cases(case_directory)
    print(f"Loaded {len(cases)} versioned Profiler evaluation cases.")

if __name__ == "__main__":
    main()
