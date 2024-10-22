from typing import List, Optional
from llms.llm import Message
from utils.pubsub import PubSub
from memory.vector_store import Record, VectorStore


class MemoryEngine:
    pubsub: PubSub
    vector_store: Optional[VectorStore]
    messages: List[Message]

    current_memory: List[Record] = []
    proposed_memory: List[Record] = []

    def __init__(self, pubsub: PubSub, vector_store: Optional[VectorStore]) -> None:
        self.pubsub = pubsub
        self.vector_store = vector_store

    def sync_messages(self, messages: List[Message]):
        self.messages = messages

    def get_memory(self):
        # get the current memory
        if len(self.messages) == 0:
            return "Memory is empty"
        pass

    def evaluate_memory(self):
        # go through proposed memory, and choose memories which seem most useful
        pass

    def propose_memory(self):
        if not self.vector_store:
            return "No memory available."
        # semantic search the database based on the current context
        if len(self.messages) == 0 or not self.messages[-1].content:
            return "No memory available."
        memory = self.vector_store.query_store(self.messages[-1].content)
        self.proposed_memory = memory

    def delete_memories(self, memories: List[int]):
        # wipe the memory
        pass
