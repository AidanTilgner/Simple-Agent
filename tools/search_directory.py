from typing import Any
import os
import re
from tools.index import Tool
from utils.pubsub import PubSub


def run(ps: PubSub, args: Any):
    if not args or 'directory_path' not in args or 'content' not in args or 'type' not in args:
        return "Error running search_directory: Missing required arguments."

    directory_path = args["directory_path"]
    search_content = args["content"]
    search_type = args["type"]
    file_extension = args.get("file_extension", None)  # Optional file extension filter
    max_results = args.get("max_results", None)  # Optional limit on the number of matches

    matching_files = []
    match_count = 0  # Track number of matches

    try:
        # Compile regex outside loop for efficiency in case of regex search
        regex_pattern = re.compile(search_content) if search_type == "regex" else None

        for root, _, files in os.walk(directory_path):
            for file in files:
                # Filter by file extension if provided
                if file_extension and not file.endswith(file_extension):
                    continue

                file_path = os.path.join(root, file)

                # Try opening the file and reading content in chunks
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        for line in f:
                            if search_type == "text-case-sensitive" and search_content in line:
                                matching_files.append(file_path)
                                match_count += 1
                                break
                            elif search_type == "text-case-insensitive" and search_content.lower() in line.lower():
                                matching_files.append(file_path)
                                match_count += 1
                                break
                            elif search_type == "regex" and regex_pattern.search(line):
                                matching_files.append(file_path)
                                match_count += 1
                                break

                except Exception as file_error:
                    # Handle individual file read errors (e.g., permissions)
                    ps.publish(f"Error reading file {file_path}: {file_error}")
                    continue

                # Stop if max_results is reached
                if max_results and match_count >= max_results:
                    break
            if max_results and match_count >= max_results:
                break

        if matching_files:
            return f"Matching files:\n{chr(10).join(matching_files)}"
        else:
            return "No matching files found."

    except Exception as e:
        return f"Error searching directory: {e}"


search_directory = Tool(
    name="search_directory",
    description="Search a directory for content of a given type.",
    function=run,
    parameters={
        "type": "object",
        "properties": {
            "directory_path": {
                "type": "string",
                "description": "The path to the directory to search.",
            },
            "content": {
                "type": "string",
                "description": "The content to search for.",
            },
            "type": {
                "type": "string",
                "enum": ["text-case-sensitive", "text-case-insensitive", "regex"],
                "description": "The type of search to perform.",
            },
            "file_extension": {
                "type": "string",
                "description": "Optional file extension filter (e.g., '.txt').",
            },
            "max_results": {
                "type": "integer",
                "description": "Optional maximum number of matching files to return.",
            },
        },
        "required": ["directory_path", "content", "type"],
    },
)
