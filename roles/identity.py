from typing import Any, Dict, List
from llms.llm import LLM
from roles.index import Role
from utils.pubsub import PubSub
from tools.index import Tool, Toolbox
from roles.core.general import GENERAL_ASSISTANT
from roles.core.developer import DEVELOPER
from roles.core.researcher import RESEARCHER
from rich.console import Console

console = Console()


class IdentityManager:
    current_role: Role = GENERAL_ASSISTANT
    available_roles: Dict[str, Role] = {
        "General Assistant": GENERAL_ASSISTANT,
        "Developer": DEVELOPER,
        "Researcher": RESEARCHER,
    }
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
            tool_description = ""
            for tool in role.get_tools_listed():
                tool_description += f"**{tool.name}**: {tool.description}\n"
            description += f"""## {role.name}
            **Identity**:
            {role.identity}

            **Tools**:
            {tool_description}
            """
        return description

    def register_role_tools(self, role: Role) -> None:
        self.toolbox.register_tools(role.get_tools_listed())

    def unregister_role_tools(self, role: Role) -> None:
        self.toolbox.unregister_tools(role.get_tools_listed())

    def set_role(self, role_name: str) -> None:
        console.print(f"Setting role to {role_name}...", style="bold green")
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

    def add_roles_to_system_prompt(self, llm: LLM):
        prompt = f"""
        # Available Roles
        {self.get_roles_described()}
        """
        llm.append_to_system_prompt(prompt)
