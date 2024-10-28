from typing import Any, List, Optional
from llms.llm import LLM, Message
from tools.index import Tool
from utils.pubsub import PubSub
from memory.vector_store import Record, VectorStore
from rich.console import Console

console = Console()


class MemoryEngine:
    pubsub: PubSub
    vector_store: Optional[VectorStore]
    messages: List[Message]
    llm: LLM

    current_memory: List[Record] = []
    proposed_memory: List[Record] = []

    def __init__(
        self, pubsub: PubSub, vector_store: Optional[VectorStore], llm: LLM
    ) -> None:
        self.pubsub = pubsub
        self.vector_store = vector_store
        self.llm = llm

    def sync_messages(self, messages: List[Message]):
        self.messages = messages

    def get_memory(self):
        # get the current memory
        if len(self.messages) == 0:
            return "Memory is empty"
        pass

    def evaluate_memory(self):
        # go through proposed memory, and choose memories which seem most useful
        self.propose_memory()
        self.delete_memories([])
        self.commit_memory()

    def propose_memory(self):
        if not self.vector_store:
            return "No memory available."
        if len(self.messages) == 0 or not self.messages[-1].content:
            return "No memory available."
        last_content = self.messages[-1].content
        if not last_content:
            return
        memory = self.vector_store.query(last_content)
        self.proposed_memory = memory

    def commit_memory(self):
        self.current_memory = self.proposed_memory

    def delete_memories(self, memories: List[int]):
        # wipe the memory
        self.current_memory = []

    def add_memory(self, memory: Record):
        if not self.vector_store:
            return "No memory available."
        self.vector_store.add_record(memory)
        return memory

    def run_decisive_memory_addition(self):
        if len(self.messages) == 0:
            return
        messages = [
            Message(
                id=None,
                role="system",
                content=f"""
                You are subconscious memory. Your job is to take context of a conversation, and manage memory.
                Based on the context, you must first decide whether there's anything worth remembering.
                If there is, use the tools provided to add the memory.
                If there isn't, do nothing.

                Here's the context:
                ---
                {self.messages[-1].content}
                ---
                """,
                tool_calls=None,
                tool_call_id=None,
            )
        ]
        with console.status("[bold purple]Memory working...", spinner="dots12"):
            self.llm.get_response(
                messages, [self.add_memory_tool(), self.dont_add_memory_tool()]
            )

    def add_memory_tool(self) -> Tool:
        def run(pubsub: PubSub, args: Any):
            content = args.get("content")
            title = args.get("title")
            importance = args.get("importance")
            type = args.get("type")

            if not title:
                return "Error adding memory: No title provided."

            if not content:
                return "Error adding memory: No content provided."

            if not type:
                return "Error adding memory: No type provided."

            if not importance:
                return "Error adding memory: No importance provided."

            memory = Record(
                id=None,
                title=title,
                content=content,
                importance=importance,
                type=type,
                similarity=None,
            )
            result = self.add_memory(memory)
            if isinstance(result, str) and result.startswith("No memory available"):
                return result
            return f"Memory added with content: {content}"

        return Tool(
            name="add_memory",
            description="Use this tool to add a new memory.",
            function=run,
            parameters={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "The title of the memory to add.",
                    },
                    "content": {
                        "type": "string",
                        "description": "The content of the memory to add.",
                    },
                    "importance": {
                        "type": "integer",
                        "description": "The importance of the memory to add. Ranges from 1 to 3. 1 is the least important, 3 is the most important.",
                    },
                    "type": {
                        "type": "string",
                        "description": "The type of the memory this is considered. Either semantic or episodic.",
                    },
                },
                "required": ["title", "content", "importance", "type"],
            },
        )

    def dont_add_memory_tool(self) -> Tool:
        def run(pubsub: PubSub, args: Any):
            return "No memory added."

        return Tool(
            name="dont_add_memory",
            description="Use this tool to skip adding a new memory.",
            function=run,
            parameters={},
        )
