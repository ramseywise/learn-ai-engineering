"""One loader per key at a time, with failures shared. Chapter 3."""
import threading
from dataclasses import dataclass, field
from typing import Any, Callable

@dataclass
class _Flight:
    event: threading.Event = field(default_factory=threading.Event)
    value: Any = None
    error: BaseException | None = None

class SingleFlight:

    def __init__(self) -> None:
        """Set up whatever state you need."""
        raise NotImplementedError()

    def do(self, key: str, load: Callable[[], Any]) -> Any:
        """Return load()'s result. Concurrent callers for one key share one call.

        If the load raises, every waiter gets that exception. The next call
        after a flight has ended starts a new load.
        """
        raise NotImplementedError()
