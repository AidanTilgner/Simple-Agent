from dataclasses import dataclass
from typing import Any, List

from rich.console import Console

from llms.llm import LLM
from tools.index import Tool
from utils.pubsub import PubSub

console = Console()

@dataclass
class Task:
    id: str
    description: str
    requirements: List[str]
    completed: bool


class Agency:
    pubsub: PubSub
    llm: LLM
    tasks: List[Task]

    def __init__(self, pubsub: PubSub, llm: LLM) -> None:
        self.pubsub = pubsub
        self.llm = llm
        self.tasks = []

    def get_new_task_id(self) -> str:
        return f"task_{len(self.tasks) + 1}"

    def get_incomplete_tasks(self) -> List[Task]:
        return [t for t in self.tasks if not t.completed]

    def get_completed_tasks(self) -> List[Task]:
        return [t for t in self.tasks if t.completed]

    def has_incomplete_tasks(self) -> bool:
        return any(not t.completed for t in self.tasks)

    def get_tasks_described(self, tasks: List[Task]):
        description = ""
        for task in tasks:
            description += "---"
            description += f"Task ID: {task.id}\n"
            description += f"Description: {task.description}\n"
            description += "Requirements: {}\n".format(
                "\n".join([f"- {req}" for req in task.requirements])
            )
            description += f"Completed: {task.completed}\n\n"
            description += "---"
        return description

    def get_incomplete_tasks_described(self):
        return self.get_tasks_described(self.get_incomplete_tasks())

    def create_task(self, description: str, requirements: List[str], completed: bool):
        id = self.get_new_task_id()
        task = Task(
            id=id,
            description=description,
            requirements=requirements,
            completed=completed,
        )
        self.tasks.append(task)
        console.print(f"Created task {id} with description: {description}", style="italic green")
        self.pubsub.publish("task_created", task)

    def complete_task(self, task_id: str):
        task = next((t for t in self.tasks if t.id is task_id), None)
        if not task:
            self.pubsub.publish("error", f"Task not found for id: {task_id}")
            return
        task.completed = True
        console.print(f"Completed task {task_id}", style="bold green")
        self.pubsub.publish("task_completed", task)

    def create_task_tool(self) -> Tool:
        def run(pubsub: PubSub, args: Any):
            description = args.get("description")
            requirements = args.get("requirements")
            completed = args.get("completed") or False
            id = self.get_new_task_id()

            if not description:
                return "Error creating task: No description provided."
            if not requirements:
                return "Error creating task: No requirements provided."
            if not isinstance(requirements, list):
                return "Error creating task: Requirements must be a list."
            if not completed:
                return "Error creating task: No completion status provided."

            self.create_task(description, requirements, completed)
            return f"Task created with id {id}."

        return Tool(
            name="create_task",
            description="Use this tool to create a new task.",
            function=run,
            parameters={
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "A description of the overall task.",
                    },
                    "requirements": {
                        "type": "array",
                        "description": "A list of requirements for the task.",
                        "items": {"type": "string"},
                    },
                    "completed": {
                        "type": "boolean",
                        "description": "Whether the task is currently completed. Defaults to False.",
                    },
                },
                "required": ["description", "requirements"],
            },
        )

    def complete_task_tool(self) -> Tool:
        def run(pubsub: PubSub, args: Any):
            task_id = args.get("task_id")
            if task_id is None:
                return f"Task with id {task_id} not found."
            self.complete_task(task_id)
            return f"Task with id {task_id} marked as complete."

        return Tool(
            name="complete_task",
            description="Use this to mark a task complete.",
            function=run,
            parameters={
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "The id of the task to complete.",
                    },
                },
                "required": ["task_id"],
            },
        )
