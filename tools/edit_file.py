from typing import Any

from tools.index import Tool
from utils.pubsub import PubSub


def run(pubsub: PubSub, args: Any):
    if not args:
        return "Error running edit_file: No arguments provided."
    with open(args["file_path"], "r") as file:
        content = file.read()
        start, end = args["range"].split("-")
        lines = content.split("\n")
        lines[int(start) - 1 : int(end)] = [args["replacement"]]
        new_content = "\n".join(lines)
    with open(args["file_path"], "w") as file:
        file.write(new_content)
    return f"File edited with new content: {new_content}"


edit_file = Tool(
    name="edit_file",
    description="Edit a file",
    function=run,
    parameters={
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "The path to the file to edit.",
            },
            "range": {
                "type": "string",
                "pattern": "^d+-d+$",
                "description": "The line numbers to edit. Formatted as 'start-end'.",
            },
            "replacement": {
                "type": "string",
                "description": "The text to replace the selected range with.",
            },
        },
        "required": ["file_path", "range", "replacement"],
    },
)
