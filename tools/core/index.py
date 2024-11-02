from tools.index import Kit

from .edit_file import edit_file
from .exec_command import exec_command
from .read_file import read_file
from .send_message_to_user import (
    send_message_to_user,
    prompt_user,
)
from .write_file import write_file
from .web_request import web_request
from .run_js import run_js

TOOLS = [
    edit_file,
    exec_command,
    read_file,
    send_message_to_user,
    prompt_user,
    write_file,
    web_request,
    run_js,
]
