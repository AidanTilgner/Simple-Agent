from roles.index import Role
from tools.core.index import TOOLS
from tools.index import Toolbox

DEFAULT_ROLE = Role(
    name="Default",
    identity="Default mode, with basic tooling for generic tasks.",
    tools=TOOLS,
)
