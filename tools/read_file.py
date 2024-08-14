from typing import Any

from tools.index import Tool
from utils.pubsub import PubSub


def run(ps: PubSub, args: Any):
    if not args:
        return "Error running send_message_to_user: No message provided."
    with open(args["file_path"], "r") as file:
        content = file.read()
        return content
    return "File not read."


read_file = Tool(
    name="read_file",
    description="Read a file",
    function=run,
    parameters={
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "The path to the file to read.",
            },
        },
        "required": ["file_path"],
    },
)
