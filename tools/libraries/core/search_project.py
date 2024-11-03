from typing import Any
import re
from tools.index import Tool
from utils.pubsub import PubSub


def run(args: Any, ps: PubSub):
    try:
        query = args.get("query")
        case_sensitive = args.get("case_sensitive", False)
        whole_word = args.get("whole_word", False)
        regex = args.get("regex", False)

        # Sample file content for demonstration purposes
        sample_file_content = "Lorem ipsum dolor sit amet, consectetur adipiscing elit."

        # Determine the flags for the regex search
        flags = re.IGNORECASE if not case_sensitive else 0

        # Modify the query for whole word matching
        if whole_word:
            query = f"\\b{query}\\b"

        # Compile the regex pattern
        pattern = re.compile(query, flags) if regex else re.compile(re.escape(query), flags)

        # Perform search
        matches = pattern.findall(sample_file_content)
        return f"Found {len(matches)} matches for the query '{query}'."
    except Exception as e:
        return f"Error searching for the query: {e}"


search_project = Tool(
    name="search_project",
    description="Performs a file search similar to 'Ctrl + Shift + F' in IDEs, with support for capitalization, matching whole words, and regex.",
    function=run,
    parameters={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "The search keyword or pattern."},
            "case_sensitive": {"type": "boolean", "description": "Whether the search is case sensitive.", "default": False},
            "whole_word": {"type": "boolean", "description": "Whether to match the whole word only.", "default": False},
            "regex": {"type": "boolean", "description": "Whether to use regex for the search.", "default": False}
        },
        "required": ["query"]
    }
)
