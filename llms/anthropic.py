import json
from dataclasses import dataclass
import os
from typing import Dict, cast, List

from anthropic.types.message_create_params import ToolChoiceToolChoiceAny
from dotenv import load_dotenv

from llms.llm import LLM, Message
from tools.index import Tool, ToolCall
from anthropic import Anthropic
from anthropic.types import (
    ContentBlock,
    TextBlockParam,
    ToolParam,
    ToolUseBlock,
    ToolUseBlockParam,
    MessageParam,
    ToolResultBlockParam,
)

load_dotenv()

anthropic_client: Anthropic
anthropic_model = "claude-3-5-sonnet-20240620"


@dataclass
class AnthropicTool:
    name: str
    description: str
    input_schema: Dict[str, object]


def init_anthropic_llm():
    global anthropic_client
    global anthropic_model

    anthropic_client = Anthropic(
        api_key=os.environ.get("ANTHROPIC_API_KEY"),
    )

    if os.environ.get("ANTHROPIC_MODEL"):
        anthropic_model = os.environ.get(
            "ANTHROPIC_MODEL", "claude-3-5-sonnet-20240620"
        )


def tool_to_anthropic_tool_call(tool: Tool) -> ToolParam:
    return ToolParam(
        name=tool.name,
        description=tool.description,
        input_schema=tool.parameters,
    )


def anthropic_tool_call_to_tool_call(tool_call: ToolUseBlock) -> ToolCall:
    tool_call_arguments_dict = (
        tool_call.input
        if isinstance(tool_call.input, dict)
        else tool_call.input.__dict__
    )
    return ToolCall(
        name=tool_call.name, arguments=tool_call_arguments_dict, id=tool_call.id
    )


def message_to_anthropic_message(message: Message) -> MessageParam:
    if not message.content and message.tool_calls:
        return MessageParam(
            content=[
                cast(
                    ContentBlock,
                    ToolUseBlockParam(
                        type="tool_use",
                        name=tool_call.name,
                        id=tool_call.id,
                        input=tool_call.arguments,
                    ),
                )
                for tool_call in message.tool_calls
            ],
            role="assistant",
        )
    if message.role == "tool":
        return MessageParam(
            content=[
                cast(
                    ToolResultBlockParam,
                    {
                        "tool_use_id": message.tool_call_id,
                        "type": "tool_result",
                        "content": message.content,
                    },
                )
            ],
            role="user",
        )
    if message.role == "user" and message.content:
        return MessageParam(
            content=[
                cast(
                    ContentBlock,
                    TextBlockParam(
                        type="text",
                        text=message.content,
                    ),
                )
            ],
            role=message.role,
        )

    if message.role == "assistant":
        return MessageParam(
            content=[
                cast(
                    ContentBlock,
                    TextBlockParam(
                        type="text",
                        text=message.content if message.content else "",
                    ),
                )
            ],
            role=message.role,
        )

    if message.role == "system":
        return MessageParam(
            content=[
                cast(
                    ContentBlock,
                    TextBlockParam(
                        type="text",
                        text=f"""SYSTEM MESSAGE:
                    {message.content if message.content else ""}
                    """,
                    ),
                )
            ],
            role="user",
        )
    return MessageParam(
        content=[
            cast(
                ContentBlock,
                TextBlockParam(
                    type="text",
                    text="",
                ),
            )
        ],
        role="user",
    )


def anthropic_message_content_to_message_content(content: List[ContentBlock]) -> str:
    return " ".join([block.text for block in content if block.type == "text"])


def ensure_alternating_roles(messages: List[MessageParam]) -> List[MessageParam]:
    new_messages: List[MessageParam] = []

    for message in messages:
        if new_messages and new_messages[-1]["role"] == message["role"]:
            new_messages[-1]["content"] = cast(
                List[ContentBlock],
                cast(List[ContentBlock], new_messages[-1]["content"])
                + cast(List[ContentBlock], message["content"]),
            )
        else:
            new_messages.append(message)

    return new_messages


def get_anthropic_model_response(
    messages: List[Message], tools: List[Tool], system_prompt: str
) -> Message:
    if not anthropic_client:
        raise ValueError("Anthropic client not initialized")

    tool_list = [tool_to_anthropic_tool_call(tool) for tool in tools]
    formatted_messages = ensure_alternating_roles(
        [message_to_anthropic_message(message) for message in messages]
    )

    message = anthropic_client.messages.create(
        model=anthropic_model,
        max_tokens=int(os.environ.get("MAX_TOKENS", 1024)),
        messages=formatted_messages,
        tools=tool_list,
        tool_choice=ToolChoiceToolChoiceAny(type="any"),
    )

    if message.stop_reason == "tool_use":
        return Message(
            id=message.id,
            role="assistant",
            content=None,
            tool_calls=[
                anthropic_tool_call_to_tool_call(cast(ToolUseBlock, tc))
                for tc in message.content
            ],
        )

    if message.stop_reason == "max_tokens":
        return Message(
            id=message.id,
            role="assistant",
            content=f"Max tokens reached. {anthropic_message_content_to_message_content(message.content)}"
            if message.content
            else "Max tokens reached.",
            tool_calls=None,
        )

    return Message(
        id=message.id,
        content=anthropic_message_content_to_message_content(message.content),
        role="assistant",
        tool_calls=None,
        tool_call_id=None,
    )


AnthropicLLM = LLM(
    name="Anthropic",
    model_name=anthropic_model,
    get_model_response=get_anthropic_model_response,
    on_startup=init_anthropic_llm,
)
