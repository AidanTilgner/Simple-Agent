from typing import Any, Callable, Dict, List


class PubSub:
    subscribers: Dict[str, List[Callable[[Any], None]]]

    def __init__(self) -> None:
        # Dictionary to hold event names and their corresponding subscribers
        self.subscribers: Dict[str, List[Callable[[Any], None]]] = {}

    def subscribe(self, event_type: str, handler: Callable[[Any], None]) -> None:
        """Adds a subscriber (handler) to an event type."""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)

    def unsubscribe(self, event_type: str, handler: Callable[[Any], None]) -> None:
        """Removes a subscriber (handler) from an event type."""
        if event_type in self.subscribers:
            self.subscribers[event_type].remove(handler)
            if not self.subscribers[event_type]:
                del self.subscribers[event_type]

    def publish(self, event_type: str, data: Any) -> None:
        """Publishes an event to all subscribers of that event type."""
        if event_type in self.subscribers:
            for handler in self.subscribers[event_type]:
                handler(data)
