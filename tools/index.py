from dataclasses import dataclass
from typing import Any, Callable, Dict

from utils.pubsub import PubSub


@dataclass
class Tool:
    name: str
    description: str
    function: Callable[
        [PubSub, Any], (str)
    ]  # Callable that takes any arguments and returns any type
    parameters: Dict[str, Any]  # Dictionary with string keys and values of any type


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: Dict[str, Any]
