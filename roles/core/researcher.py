from roles.index import Role
from tools.core.index import web_request, write_file, run_js

TOOLS = [web_request, write_file, run_js]

RESEARCHER = Role(
    name="Researcher",
    identity="A dedicated researcher with specialized tools for web research, data analysis, and documentation.",
    tools=TOOLS,
)
