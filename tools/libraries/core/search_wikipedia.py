from typing import Any
from tools.index import Tool
from goodwiki import GoodwikiClient
from utils.pubsub import PubSub
import asyncio

client = GoodwikiClient()


async def fetch_page(query: str):
    try:
        page = await client.get_page(query, with_styling=True)

        # Check if 'pageid' key is present to avoid KeyError
        if page.pageid is None:
            return None  # Or return an appropriate error message

        return page
    except KeyError:
        # Log or handle cases where 'pageid' or other keys are missing
        return None
    except Exception as e:
        # Catch any other exceptions to prevent the entire program from crashing
        print(f"An error occurred while fetching the page: {e}")
        return None


def run_search_wikipedia(args: Any, pubsub: PubSub) -> str:
    try:
        if not args or "query" not in args:
            return "Error running search_wikipedia: No query provided."

        # Explicitly create and set a new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        page = loop.run_until_complete(fetch_page(args.get("query")))
        loop.close()  # Close the event loop when done to prevent resource leaks

        if not page:
            return "No articles found for the given query."

        results = f"""Results for search query: {args.get("query")}
        {page.title}
        ---
        {page.markdown}
        ---
        """

        truncated_results = results[:5000]
        return truncated_results
    except Exception as e:
        return f"Error running search_wikipedia: {e}"


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
