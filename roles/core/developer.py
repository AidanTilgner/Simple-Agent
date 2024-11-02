from roles.index import Role
from tools.core.index import web_request, write_file, run_js, edit_file
from tools.index import Tool

TOOLS = [web_request, write_file, run_js, edit_file]

DEVELOPER = Role(
    name="Developer",
    identity="""
    A dedicated developer with tools for developing software, building applications, managing projects, and debugging.
    """,
    tools=TOOLS,
)
