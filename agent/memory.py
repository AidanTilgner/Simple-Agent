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

    def is_setup(self) -> bool:
        if self.vector_store is None:
            return False
        if self.llm is None:
            return False
        return True

    def sync_messages(self, messages: List[Message]):
        self.messages = messages

    def get_memory(self) -> str:
        # get the current memory
        if len(self.messages) == 0:
            return "Memory is empty"
        memory = """
        Title | Type | Content
        """
        for record in self.current_memory:
            memory += f"""
            {record.title} | {record.type} | {record.content}
            """
        return memory

    def evaluate_memory(self):
        # go through proposed memory, and choose memories which seem most useful
        self.propose_memory()
        self.delete_memories([])
        self.commit_memory()

    def get_context(self):
        context = ""
        for content in [
            m.content
            for m in self.messages
            if m.content is not None and m.role in ["user", "system", "tool"]
        ]:
            context += content + " "
        return context

    def propose_memory(self):
        if not self.vector_store:
            return "No memory available."
        if len(self.messages) == 0 or not self.messages[-1].content:
            return "No memory available."
        context = self.get_context()
        if not context:
            return
        memory = self.vector_store.query(context)
        self.proposed_memory = memory

    def commit_memory(self):
        self.current_memory = self.proposed_memory

    def delete_memories(self, memories: List[int]):
        # wipe the memory
        self.current_memory = []

    def add_memory(self, memory: Record):
        if not self.vector_store:
            return "Error: Tried to add memory when memory not initialized."
        self.vector_store.add_record(memory)
        console.print(
            f"Remembered: [italic]{memory.title}[/italic]", style="medium_orchid3"
        )
        return memory

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
            if isinstance(result, str) and result.startswith("Error"):
                return "Something went wrong." + result
            return f"Memory added: {title}"

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
                        "description": "The importance of the memory between 1 and 5. 1 being unimportant and unuseful, 5 being very important and useful.",
                    },
                    "type": {
                        "type": "string",
                        "pattern": "^(semantic|episodic)$",
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
