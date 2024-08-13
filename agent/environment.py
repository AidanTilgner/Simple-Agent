from typing import List

from utils.pubsub import PubSub

unseen_messages = []


class Environment:
    pubsub: PubSub

    unseen_messages: List[str] = []

    def __init__(self, pubsub: PubSub) -> None:
        self.pubsub = pubsub

        self.listen_to_messages()

    def listen_to_messages(self):
        self.pubsub.subscribe(
            "new_user_message", lambda message: self.unseen_messages.append(message)
        )

    def get_environment(self):
        unseen_messages = self.unseen_messages
        self.unseen_messages = []

        if len(unseen_messages) == 0:
            return ""

        return f"""
        Unseen Messages:
        {[message for message in unseen_messages]}\n
        """

    def new_perception(self):
        return len(self.unseen_messages) > 0
