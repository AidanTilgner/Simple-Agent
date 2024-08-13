from utils.pubsub import PubSub


class Memory:
    pubsub: PubSub

    def __init__(self, pubsub):
        self.pubsub = pubsub

    def search_memory(self, context: str):
        """
        This is where the memory of the agent will be queried.
        """
        return "Memory is empty."

    def add_to_memory(self, label: str, context: str):
        """
        This is where the memory of the agent will be updated.
        """
        return "Memory Updated."
