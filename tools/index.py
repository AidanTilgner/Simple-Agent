from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

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


class Toolbox:
    pubsub: Optional[PubSub] = None
    tools: Dict[str, Tool] = {}

    def __init__(self, pubsub: PubSub) -> None:
        self.pubsub = pubsub

    def get_tools_listed(self) -> List[Tool]:
        return list(self.tools.values())

    def get_tool(self, tool_name: str) -> Optional[Tool]:
        return self.tools.get(tool_name)

    def tool_log(self, tool_name: str, message: str, arguments: Any = None):
        if not self.pubsub:
            raise Exception("No PubSub provided.")
        self.pubsub.publish(
            "toolbox_log", f'Ran {tool_name}({arguments}) and result "{message}"'
        )

    def run_tool(self, tool_name: str, arguments: Any) -> str:
        if not self.pubsub:
            raise Exception("No PubSub provided.")
        tool = self.get_tool(tool_name)
        if not tool:
            self.pubsub.publish("toolbox_error", f"Tool '{tool_name}' not found.")
            return "Tool not found."
        message = tool.function(self.pubsub, arguments)
        self.tool_log(tool_name, message, arguments)
        return message

    def register_tool(self, tool: Tool):
        try:
            self.tools[tool.name] = tool
        except Exception as e:
            raise Exception(f"Error registering tool: {e}")

    def unregister_tool(self, tool: Tool):
        if tool.name in self.tools:
            try:
                del self.tools[tool.name]
            except KeyError:
                raise Exception(f"Error unregistering tool: Tool '{tool.name}' not found.")
        else:
            raise Exception(f"Error unregistering tool: Tool '{tool.name}' not found.")

    def register_tools(self, tools: List[Tool]):
        try:
            for tool in tools:
                self.register_tool(tool)
        except Exception as e:
            raise Exception(f"Error registering tools: {e}")

    def unregister_tools(self, tools: List[Tool]):
        try:
            for tool in tools:
                self.unregister_tool(tool)
        except Exception as e:
            raise Exception(f"Error unregistering tools: {e}")
