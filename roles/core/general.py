from roles.index import Role
from tools.core.index import (
    edit_file,
    exec_command,
    read_file,
    write_file,
)

TOOLS = [
    edit_file,
    exec_command,
    read_file,
    write_file,
]

GENERAL_ASSISTANT = Role(
    name="General Assistant",
    identity="A general assistant that can help with a variety of simple tasks.",
    tools=TOOLS,
)
