# Adding a Role
Roles are ways to specialize the agent's functionality, by allowing the agent to dynamically switch between roles depending on the task at hand. Each role contains a set of tools which are useful to that domain. While the core roles may be accomidating to your needs, you may be inclined to create entirely new roles.

> [!note]
> If you're looking to add functionality to an existing role, consider checking out the [Adding a Tool](./adding-a-tool.md) guide.

## Roles, briefly

A Role is utilized by the agent to determine which tools are available to it. The agent only has access to the tools that are defined under the role that is currently adopted. Multiple Roles can use the same tools, and a Role can have multiple tools. A Role is defined as a `Role` object, which contains a name, identity, and a list of tools. You can find the `Role` object defined in the `roles/index.py` file. It looks like this:

```python
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
```

By default, there are already multiple roles defined under `roles/core/`, which you can freely modify to your hearts content. For example, the Developer role is defined in `roles/core/developer.py`. In this file, you'll find the `Developer` role defined as follows:

```python
from roles.index import Role
from tools.libraries.core.web_request import web_request
from tools.libraries.core.write_file import write_file
from tools.libraries.core.run_js import run_js
from tools.libraries.core.edit_file import edit_file
from tools.libraries.core.exec_command import exec_command
from tools.libraries.core.read_file import read_file

TOOLS = [web_request, write_file, run_js, edit_file, exec_command, read_file]

DEVELOPER = Role(
    name="Developer",
    identity="""
    A dedicated developer with tools for developing software, building applications, managing projects, and debugging.
    """,
    tools=TOOLS,
)
```

## Adding a new Role

The `roles/config.py` file is where all of the configuration regarding roles in Simple Agent is handled. You can find the `ROLES_INCLUDED` list defined in this file, which contains all of the roles that are included in the agent. To add a new role, you would simply add an instance of the `Role` class to this list.

To define the role which the agent starts with, you can find the `DEFAULT_ROLE` variable defined in the `roles/config.py`, which is set to `GENERAL_ASSISTANT` by default, but can be changed to any role you'd like.
