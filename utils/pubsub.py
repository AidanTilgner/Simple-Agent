import threading
from typing import Any, Callable, Dict, List


class PubSub:
    def __init__(self) -> None:
        # Dictionary to hold event names and their corresponding subscribers
        self.subscribers: Dict[str, List[Callable[[Any], None]]] = {}
        # Lock to ensure thread-safe operations
        self.lock = threading.Lock()

    def subscribe(self, event_type: str, handler: Callable[[Any], None]) -> None:
        """Adds a subscriber (handler) to an event type."""
        with self.lock:
            if event_type not in self.subscribers:
                self.subscribers[event_type] = []
            self.subscribers[event_type].append(handler)

    def unsubscribe(self, event_type: str, handler: Callable[[Any], None]) -> None:
        """Removes a subscriber (handler) from an event type."""
        with self.lock:
            if event_type in self.subscribers:
                self.subscribers[event_type].remove(handler)
                if not self.subscribers[event_type]:
                    del self.subscribers[event_type]

    def publish(self, event_type: str, data: Any) -> None:
        """Publishes an event to all subscribers of that event type."""
        subscribers_copy = []
        with self.lock:
            if event_type in self.subscribers:
                # Copy the subscriber list to avoid issues if subscribers are modified during iteration
                subscribers_copy = self.subscribers[event_type][:]

        # Invoke handlers outside the locked region to avoid potential deadlocks and to allow concurrent handling
        for handler in subscribers_copy:
            handler(data)
