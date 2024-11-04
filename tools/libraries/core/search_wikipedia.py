from typing import Any, Dict, List
from tools.index import Tool
from goodwiki import GoodwikiClient
from utils.pubsub import PubSub
import asyncio

client = GoodwikiClient()

def run_search_wikipedia(args: Any, pubsub: PubSub) -> str:
    if not args or "query" not in args:
        return "Error running search_wikipedia: No query provided."

    page = asyncio.run(client.get_page(args.get("query"), with_styling=True))

    if not page:
        return "No articles found for the given query."

    return f"""Articles found for "{args.get("query")}":
    """


search_wikipedia = Tool(
    name="search_wikipedia",
    description="Search Wikipedia for information on a given query.",
    function=run_search_wikipedia,
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search term for finding relevant Wikipedia articles.",
            },
        },
        "required": ["query"],
    },
)
