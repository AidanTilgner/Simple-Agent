from dataclasses import asdict, dataclass
from typing import Callable, List, Optional

from tools.index import Tool, ToolCall


@dataclass
class Message:
    content: Optional[str]
    role: str
    tool_calls: Optional[List[ToolCall]]
    tool_call_id: Optional[str] = None

    def to_json(self):
        return asdict(self)


class LLM:
    get_model_response: Callable[[List[Message], List[Tool]], Message]
    on_startup: Optional[Callable[[], None]] = None
    name: str
    model_name: str

    def __init__(
        self,
        name,
        model_name,
        get_model_response: Callable[[List[Message], List[Tool]], Message],
        on_startup: Optional[Callable[[], None]] = None,
    ):
        self.name = name
        self.model_name = model_name
        self.get_model_response = get_model_response
        self.on_startup = on_startup

    def startup(self):
        if self.on_startup:
            self.on_startup()

    def get_response(self, messages: List[Message], tools: List[Tool]) -> Message:
        return self.get_model_response(messages, tools)

    def get_text_response(self, message: str) -> str:
        response = self.get_model_response(
            [Message(content=message, role="user", tool_calls=None)], []
        )
        if not response.content:
            return ""
        return response.content
