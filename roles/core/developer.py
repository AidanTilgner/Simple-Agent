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
