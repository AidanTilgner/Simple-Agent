from roles.index import Role
from tools.libraries.core.edit_file import edit_file
from tools.libraries.core.exec_command import exec_command
from tools.libraries.core.read_file import read_file
from tools.libraries.core.write_file import write_file
from tools.libraries.core.scraper import scraper
from tools.libraries.core.web_request import web_request
from tools.libraries.core.search_project import search_project

TOOLS = [
    edit_file,
    exec_command,
    read_file,
    write_file,
    scraper,
    web_request,
    search_project,
]

DEVELOPER = Role(
    name="Developer",
    identity="A dedicated developer with specialized tools for software development, testing, and debugging.",
    tools=TOOLS,
)
