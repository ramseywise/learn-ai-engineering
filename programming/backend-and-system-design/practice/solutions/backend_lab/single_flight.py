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
        self._lock = threading.Lock()
        self._flights: dict[str, _Flight] = {}

    def do(self, key: str, load: Callable[[], Any]) -> Any:
        """Return load()'s result. Concurrent callers for one key share one call.

        If the load raises, every waiter gets that exception. The next call
        after a flight has ended starts a new load.
        """
        with self._lock:
            flight = self._flights.get(key)
            leader = flight is None
            if leader:
                flight = self._flights[key] = _Flight()
        if not leader:
            flight.event.wait()
        else:
            try:
                flight.value = load()
            except BaseException as err:
                flight.error = err
            finally:
                with self._lock:
                    del self._flights[key]
                flight.event.set()
        if flight.error is not None:
            raise flight.error
        return flight.value
