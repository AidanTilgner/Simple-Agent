from roles.index import Role
from tools.libraries.core.edit_file import edit_file
from tools.libraries.core.exec_command import exec_command
from tools.libraries.core.read_file import read_file
from tools.libraries.core.write_file import write_file

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
