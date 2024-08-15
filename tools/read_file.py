from typing import Any

from tools.index import Tool
from utils.pubsub import PubSub


def run(ps: PubSub, args: Any):
    if not args:
        return "Error running send_message_to_user: No message provided."
    with open(args["file_path"], "r") as file:
        content = file.read()
        if args.get("with_line_numbers"):
            content = add_line_numbers(content)
        if args.get("range"):
            start, end = args["range"].split("-")
            content = "\n".join(content.split("\n")[int(start) - 1 : int(end)])
        return content
    return "File not read."


def add_line_numbers(content: str) -> str:
    lines = content.split("\n")
    lines_with_numbers = []
    for i, line in enumerate(lines):
        lines_with_numbers.append(f"{i+1}: {line}")
    return "\n".join(lines_with_numbers)


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
            "with_line_numbers": {
                "type": "boolean",
                "description": "Whether to include line numbers in the output. Good for code files. Defaults to False.",
            },
            "range": {
                "type": "string",
                "pattern": "^d+-d+$",
                "description": "The line numbers to read. Formatted as 'start-end'.",
            },
        },
        "required": ["file_path"],
    },
)
