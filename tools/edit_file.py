from typing import Any

from tools.index import Tool
from utils.formatting import parse_range
from utils.pubsub import PubSub


def run(pubsub: PubSub, args: Any):
    try:
        file_path = args.get("file_path")
        selection = args.get(
            "selection", "1-"
        )  # Default to replace entire file if selection is missing
        content = args.get("content", "")  # Default to empty content

        # Read the file lines
        with open(file_path, "r") as f:
            lines = f.readlines()

        # Parse selection
        start, end = parse_range(range=selection, length=len(lines))

        if start is None or end is None:
            return "Invalid selection range"

        # Prepare the new content
        to_insert = content.split("\n")
        new_content = "\n".join(lines[: start - 1] + to_insert + lines[end:])

        # Write the new content back to the file
        with open(file_path, "w") as f:
            f.write(new_content)

        return "File edited successfully"
    except Exception as e:
        # For better debugging, consider logging the exception with traceback
        import traceback

        traceback.print_exc()
        return f"There was an error editing the file: {e}"


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
            "selection": {
                "type": "string",
                "pattern": "^d+-d+$",
                "description": "The target line numbers to select, formatted (start-end), you may omit the end or start to select from the beginning or to the end.",
            },
            "content": {
                "type": "string",
                "description": "The content to replace the selection with.",
            },
        },
        "required": ["file_path", "selection", "content"],
    },
)
