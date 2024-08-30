import os
from typing import List
import tiktoken

from llms.llm import Message

def get_current_num_tokens(messages: List[Message], model: str):
    encoding = tiktoken.encoding_for_model(model)
    num_tokens = 0

    for message in messages:
        if message.content:
            num_tokens += 4
            num_tokens += len(encoding.encode(message.content))

    return num_tokens


def truncate_message(message: Message):
    max_message_length = int(os.environ.get("MAX_MESSAGE_LENGTH", 10000))

    if message.content and len(message.content) > max_message_length:
        message.content = message.content[:max_message_length] + "...[TRUNCATED]"

    return message
