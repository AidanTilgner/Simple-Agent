from roles.index import Role
from tools.libraries.core.read_file import read_file

TOOLS = [
    read_file,
]

HELPFUL_ASSISTANT = Role(
    name="Helpful Assistant",
    identity="A helpful assistant that can assist with a variety of tasks.",
    tools=TOOLS,
)
