from typing import Any, Dict, List
from agent.agency import Agency
from agent.memory import MemoryEngine
from roles.core.default import DEFAULT_ROLE
from tools.index import Tool, Toolbox
from utils.pubsub import PubSub
from roles.roles import ROLES


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


class IdentityManager:
    current_role: Role
    available_roles: Dict[str, Role] = {"Default": DEFAULT_ROLE}
    pubsub: PubSub
    toolbox: Toolbox

    def __init__(self, pubsub: PubSub, toolbox: Toolbox) -> None:
        self.pubsub = pubsub
        self.toolbox = toolbox

    def register_role(self, role: Role) -> None:
        self.available_roles[role.name] = role

    def unregister_role(self, role_name: str) -> None:
        if role_name in self.available_roles:
            del self.available_roles[role_name]
        else:
            raise Exception(f"Role {role_name} not found.")

    def register_roles(self, roles: List[Role]) -> None:
        for role in roles:
            self.register_role(role)

    def unregister_roles(self, role_names: List[str]) -> None:
        for role_name in role_names:
            self.unregister_role(role_name)

    def get_roles_listed(self) -> List[Role]:
        return list(self.available_roles.values())

    def get_roles_described(self) -> str:
        description = ""
        for role in self.available_roles.values():
            description += f"{role.name}: {role.identity}\n"
        return description

    def register_role_tools(self, role: Role) -> None:
        self.toolbox.register_tools(role.get_tools_listed())

    def unregister_role_tools(self, role: Role) -> None:
        self.toolbox.unregister_tools(role.get_tools_listed())

    def set_role(self, role_name: str) -> None:
        self.unregister_role_tools(self.current_role)
        gotten_role = self.available_roles.get(role_name)
        if gotten_role:
            self.current_role = gotten_role
            self.register_role_tools(self.current_role)
        else:
            raise Exception(f"Role {role_name} not found.")

    def set_role_tool(self) -> Tool:
        def run(pubsub: PubSub, args: Any):
            try:
                name = args.get("name")
                if not name:
                    return "No name provided."
                if name not in self.available_roles:
                    return f"Role {name} not found."
                self.set_role(name)
                return f"Role set to {name}."
            except Exception as e:
                return f"Error setting role: {e}"

        return Tool(
            name="set_role",
            description="Set the current role.",
            function=run,
            parameters={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The name of the role to set.",
                    },
                },
                "required": ["name"],
            },
        )
