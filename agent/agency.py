from typing import List

from llms.llm import LLM, Message
from utils.pubsub import PubSub


class Agency:
    pubsub: PubSub
    llm: LLM

    def __init__(self, pubsub: PubSub, llm: LLM) -> None:
        self.pubsub = pubsub
        self.llm = llm

    def get_agency(self, messages: List[Message]):
        prompt = f"""
        Based on the following messages, please detail the following:
            1. A next step
            2. An overall goal to complete
            3. Completion criteria

        Messages:
        ---
        {[f"- {message.role}: {message.content}" for message in messages]}
        ---
        """
        response = self.llm.get_text_response(prompt)
        if not response:
            return "No agency."
        return response
