from roles.index import Role
from tools.libraries.core.read_file import read_file
from tools.libraries.core.search_duckduckgo import search_duckduckgo
from tools.libraries.core.code_interpreter import python_interpreter

TOOLS = [
    read_file,
    search_duckduckgo,
    python_interpreter,
]

HELPFUL_ASSISTANT = Role(
    name="Helpful Assistant",
    identity="A helpful assistant that can assist with a variety of tasks.",
    tools=TOOLS,
)
