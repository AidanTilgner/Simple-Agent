from typing import Any

from tools.index import Tool
from utils.pubsub import PubSub


def run(ps: PubSub, args: Any):
    if not args:
        return "Error running send_message_to_user: No message provided."
    try:
        with open(args["file_path"], "r") as file:
            content = file.read()
            content = add_line_numbers(content)
            if args.get("range"):
                start, end = args["range"].split("-")
                lines = content.split("\n")
                start = int(start) if start else 0
                end = int(end) if end else len(lines)
                content = "\n".join(lines[start - 1 : end])
            return f"File contents:\n```\n{content}\n```"
        return "File not read."
    except Exception as e:
        return f"Error reading file: {e}"


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
            "range": {
                "type": "string",
                "pattern": "^d+-d+$",
                "description": "The line numbers to read. Formatted as 'start-end'.",
            },
        },
        "required": ["file_path"],
    },
)
