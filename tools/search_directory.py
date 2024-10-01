# Simple-Agent/tools/search_directory.py
from tools.index import Tool
import os
import re
from utils.pubsub import PubSub
from typing import Any, List, Dict, Optional


def search_files(
    directory: str, pattern: str, ignore: Optional[List[str]] = None, depth: int = -1
) -> List[Dict[str, Any]]:
    matches = []
    regex = re.compile(pattern)
    ignore_set = set(ignore or [])

    def should_ignore(file_path: str) -> bool:
        return any(ignored in file_path for ignored in ignore_set)

    def get_depth(root: str) -> int:
        return root[len(directory) :].count(os.sep)

    for root, _, files in os.walk(directory):
        if depth != -1 and get_depth(root) > depth:
            continue
        for file in files:
            file_path = os.path.join(root, file)
            if should_ignore(file_path):
                continue
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    for match in regex.finditer(content):
                        matches.append(
                            {
                                "file": file_path,
                                "line": match.string.splitlines().index(match.group(0))
                                + 1,
                                "match": match.group(0),
                            }
                        )
            except Exception as e:
                matches.append({"file": file_path, "error": str(e)})

    return matches


def run(ps: PubSub, args: Any):
    if not args or "directory" not in args:
        return "Error running search_directory: No directory provided."
    if "pattern" not in args:
        return "Error running search_directory: No pattern provided."

    directory = args["directory"]
    pattern = args["pattern"]
    ignore = args.get("ignore", [])
    depth = args.get("depth", -1)

    try:
        results = search_files(directory, pattern, ignore, depth)
        return f"Search results:\n```\n{results}\n```"
    except Exception as err:
        return f"Error occurred: {err}"


search_directory = Tool(
    name="search_directory",
    description="Search for a pattern in files within a given directory. Returns list of matches.",
    function=run,
    parameters={
        "type": "object",
        "properties": {
            "directory": {
                "type": "string",
                "description": "The directory to search in.",
            },
            "pattern": {
                "type": "string",
                "description": "The regex pattern to search for in the files.",
            },
            "ignore": {
                "type": "array",
                "items": {
                    "type": "string",
                },
                "description": "List of files or directories to ignore.",
            },
            "depth": {
                "type": "integer",
                "description": "The maximum depth to search. -1 for unlimited depth.",
                "default": -1,
            },
        },
        "required": ["directory", "pattern"],
    },
)
