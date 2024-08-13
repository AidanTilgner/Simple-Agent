from typing import Any, Dict, List, Optional

from tools.index import Tool
from tools.send_message_to_user import send_message_to_user
from utils.pubsub import PubSub


def get_tools() -> Dict[str, Tool]:
    """
    This is where the tools available to the agent will be queried.
    """
    tools = {
        "send_message_to_user": send_message_to_user,
    }

    return tools


class Toolbox:
    pubsub: Optional[PubSub] = None
    tools: Dict[str, Tool] = get_tools()

    def __init__(self, ps: PubSub) -> None:
        self.pubsub = ps

    def get_tools_listed(self) -> List[Tool]:
        return list(self.tools.values())

    def get_tool(self, tool_name: str) -> Optional[Tool]:
        return self.tools.get(tool_name)

    def run_tool(self, tool_name: str, arguments: Any) -> str:
        if not self.pubsub:
            raise Exception("No PubSub provided.")
        tool = self.get_tool(tool_name)
        if not tool:
            self.pubsub.publish("toolbox_error", f"Tool '{tool_name}' not found.")
            return "Tool not found."
        return tool.function(self.pubsub, arguments)
