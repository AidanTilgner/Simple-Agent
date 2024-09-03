import json
import os
from typing import List

from dotenv import load_dotenv

from llms.llm import LLM, Message
from tools.index import Tool, ToolCall
from anthropic import Anthropic

load_dotenv()

anthropic_client: Anthropic
anthropic_model= "claude-3-5-sonnet-20240620"

def init_anthropic_llm():
    global anthropic_client
    global anthropic_model

    anthropic_client = Anthropic(
        api_key=os.environ.get("ANTHROPIC_API_KEY"),
    )

    if os.environ.get("ANTHROPIC_MODEL"):
        anthropic_model = os.environ.get("ANTHROPIC_MODEL", "claude-3-5-sonnet-20240620")


def tool_to_anthropic_tool_call(tool: Tool) -> ?:
