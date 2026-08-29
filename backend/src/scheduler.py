import signal
from threading import Event


def main() -> None:
    """Keep the scheduler alive until the M8 scheduler replaces this scaffold."""
    stop_event = Event()

    def stop(*_: object) -> None:
        stop_event.set()

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)
    print("Scheduler scaffold running", flush=True)
    stop_event.wait()


if __name__ == "__main__":
    main()
