from typing import Any

from tools.index import Tool

from utils.pubsub import PubSub


def run(ps: PubSub, args: Any):
    if not args:
        return "Error running send_message_to_user: No message provided."
    ps.publish("new_agent_message", args.content)
    return "Message sent to user."


send_message_to_user = Tool(
    name="send_message_to_user",
    description="Send a message to the user",
    function=run,
    parameters={
        "type": "object",
        "properties": {
            "content": {
                "type": "string",
                "description": "The contents of the message.",
            },
        },
        "required": ["content"],
    },
)
