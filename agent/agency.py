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
    silence_actions: bool

    def __init__(self, pubsub: PubSub, llm: LLM, silence_actions: bool) -> None:
        self.pubsub = pubsub
        self.llm = llm
        self.tasks = []
        self.silence_actions = silence_actions

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

    def create_task(
        self, description: str, requirements: List[str], completed=False
    ) -> bool:
        try:
            id = self.get_new_task_id()
            task = Task(
                id=id,
                description=description,
                requirements=requirements,
                completed=completed,
            )
            self.tasks.append(task)
            if not self.silence_actions:
                console.print(
                    f"Created task: [italic]{description}[/italic]",
                    style="green",
                )
            self.pubsub.publish("task_created", task)
            return True
        except Exception as e:
            console.print(f"Error creating task: {e}", style="bold red")
            return False

    def complete_task(self, task_id: str) -> bool:
        try:
            for task in self.tasks:
                if task.id == task_id:
                    task.completed = True
                    self.pubsub.publish("task_completed", task)
                    if not self.silence_actions:
                        console.print(
                            f"Completed task: [italic]{task.description}[/italic]",
                            style="green",
                        )
                    return True
            console.print(f"Task {task_id} not found.", style="bold red")
            return False
        except Exception as e:
            console.print(f"Error completing task: {e}", style="bold red")
            return False

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

            worked = self.create_task(description, requirements, completed)
            if not worked:
                return "Error creating task."
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
            worked = self.complete_task(task_id)
            if not worked:
                return f"Error completing task with id {task_id}."
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
