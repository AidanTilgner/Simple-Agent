from typing import List
from tools.index import Tool


class Role:
    name: str
    identity: str
    tools: List[Tool]

    def __init__(self, name: str, identity: str, tools: List[Tool]) -> None:
        self.name = name
        self.identity = identity
        self.tools = tools

    def get_tools_listed(self) -> List[Tool]:
        return self.tools
