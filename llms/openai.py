import json
import os
from typing import List

from dotenv import load_dotenv
from openai import NOT_GIVEN, OpenAI
from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,
    ChatCompletionMessageToolCall,
    ChatCompletionSystemMessageParam,
    ChatCompletionToolMessageParam,
    ChatCompletionToolParam,
    ChatCompletionUserMessageParam,
)
from openai.types.chat.chat_completion_message_tool_call_param import (
    ChatCompletionMessageToolCallParam,
    Function,
)
from openai.types.shared_params import FunctionDefinition

from llms.llm import LLM, Message
from tools.index import Tool, ToolCall

load_dotenv()

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def tool_to_openai_tool_call(tool: Tool) -> ChatCompletionToolParam:
    return ChatCompletionToolParam(
        type="function",
        function=FunctionDefinition(
            name=tool.name,
            description=tool.description,
            parameters=tool.parameters,
        ),
    )


def openai_tool_call_to_tool_call(tool_call: ChatCompletionMessageToolCall) -> ToolCall:
    parsed_arguments = json.loads(tool_call.function.arguments)
    return ToolCall(
        name=tool_call.function.name, arguments=parsed_arguments, id=tool_call.id
    )


def tool_call_to_openai_tool_call(
    tool_call: ToolCall,
) -> ChatCompletionMessageToolCallParam:
    return ChatCompletionMessageToolCallParam(
        id=tool_call.id,
        function=Function(
            name=tool_call.name, arguments=json.dumps(tool_call.arguments)
        ),
        type="function",
    )


def message_to_openai_message(message: Message) -> ChatCompletionMessageParam:
    if not message.content:
        return ChatCompletionAssistantMessageParam(
            content="",
            role="assistant",
            tool_calls=[tool_call_to_openai_tool_call(tc) for tc in message.tool_calls]
            if message.tool_calls
            else [],
        )
    if message.role == "tool" and message.tool_call_id is not None:
        return ChatCompletionToolMessageParam(
            content=message.content,
            role="tool",
            tool_call_id=message.tool_call_id,
        )
    if message.role == "user":
        return ChatCompletionUserMessageParam(
            content=message.content,
            role="user",
        )
    if message.role == "assistant":
        return ChatCompletionAssistantMessageParam(
            content=message.content,
            role="assistant",
        )
    if message.role == "system":
        return ChatCompletionSystemMessageParam(
            content=message.content,
            role="system",
        )
    raise ValueError(f"Invalid message role: {message.role}")


def get_openai_model_response(messages: List[Message], tools: List[Tool]) -> Message:
    tool_list = [tool_to_openai_tool_call(tool) for tool in tools]
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[message_to_openai_message(message) for message in messages],
        tools=tool_list if len(tool_list) > 0 else NOT_GIVEN,
    )

    message = response.choices[0].message

    if message.tool_calls is None:
        return Message(
            content=message.content,
            role=message.role,
            tool_calls=None,
            tool_call_id=None,
        )

    return Message(
        content=None,
        role=message.role,
        tool_calls=[openai_tool_call_to_tool_call(tc) for tc in message.tool_calls],
        tool_call_id=None,
    )


OpenAILLM = LLM(
    get_model_response=get_openai_model_response,
)
