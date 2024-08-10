import os
from typing import List
from openai import OpenAI
from openai.types.chat import (
    ChatCompletionMessageParam,
)

# client = OpenAI(
#     api_key=os.environ.get["OPENAI_API_KEY"],
# )

messages: List[ChatCompletionMessageParam] = []


# Perception Stage
def percieve():
    return "perception"


def remember():
    return "memory"


def form_goal():
    return "agency"


def build_prompt():
    perception = percieve()
    memory = remember()
    agency = form_goal()

    prompt = f"""
    Perception: {perception}
    Memory: {memory}
    Agency: {agency}
    """

    return prompt


# Reasoning Stage
def agent_reason():
    return "reasoning"


# Action Stage
def act():
    return "action outcome"


# LLM Utils
def add_prompt_to_messages(prompt: str):
    messages.append(
        {
            "content": prompt,
            "role": "user",
        }
    )


def add_response_to_messages(response: str):
    messages.append(
        {
            "content": response,
            "role": "assistant",
        }
    )


def agent_loop():
    pass


# TUI
def start_chat():
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Chatbot: Goodbye!")
            break
        response = "Testing..."
        print(f"Chatbot: {response}")


if __name__ == "__main__":
    start_chat()
