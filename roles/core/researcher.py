from roles.index import Role
from tools.libraries.core import read_file
from tools.libraries.core.web_request import web_request
from tools.libraries.core.write_file import write_file
from tools.libraries.core.scraper import run_javascript, run_beautiful_soup
from tools.libraries.core.search_wikipedia import search_wikipedia

TOOLS = [web_request, read_file, write_file, run_javascript, run_beautiful_soup, search_wikipedia]

RESEARCHER = Role(
    name="Researcher",
    identity="A dedicated researcher with specialized tools for web research, data analysis, and documentation.",
    tools=TOOLS,
)
