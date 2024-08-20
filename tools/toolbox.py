from typing import Any, Dict, List, Optional

from tools.edit_file import edit_file
from tools.exec_command import exec_command
from tools.index import Tool
from tools.read_file import read_file
from tools.send_message_to_user import send_message_to_user
from tools.write_file import write_file
from utils.pubsub import PubSub

DEFAULT_TOOLS = {
    "send_message_to_user": send_message_to_user,
    "read_file": read_file,
    "write_file": write_file,
    "exec_command": exec_command,
    "edit_file": edit_file,
}


class Toolbox:
    pubsub: Optional[PubSub] = None
    tools: Dict[str, Tool] = DEFAULT_TOOLS

    def __init__(self, ps: PubSub) -> None:
        self.pubsub = ps

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

    def register_tool(self, Tool):
        self.tools[Tool.name] = Tool
