import json
import threading
import time
from typing import List

from rich.console import Console

from agent.agency import Agency
from agent.environment import Environment
from agent.memory import Memory
from llms.llm import LLM, Message
from tools.toolbox import Toolbox
from utils.pubsub import PubSub

console = Console()


class Agent:
    pubsub: PubSub
    messages: List[Message] = [
        Message(
            role="system",
            content="""
            You are Simmy! A helpful agent, capable of performing tasks through interaction with and instruction by a user.

            When the user sends a message, you will see them in your environment. You can then select a choice of actions to take based on the message.
            You have tools at your disposal and **you should use them**.

            You should treat interaction with the user as an iterative process, so don't be afraid to gain clarification through sending the user a message and prompting them.

            Use the 'create_task' and 'complete_task' tools to manage tasks.
            """,
            tool_calls=None,
            tool_call_id=None,
        )
    ]
    llm: LLM
    toolbox: Toolbox
    environment: Environment
    memory: Memory
    agency: Agency
    running: bool = False
    thread: threading.Thread
    verbose: bool
    iteration: int = 0

    def __init__(
        self, pubsub: PubSub, llm: LLM, toolbox: Toolbox, verbose: bool
    ) -> None:
        self.pubsub = pubsub
        self.llm = llm
        self.toolbox = toolbox
        self.environment = Environment(pubsub)
        self.memory = Memory(pubsub)
        self.agency = Agency(pubsub, llm)
        self.thread = threading.Thread(target=self.run)
        self.verbose = verbose

        self.toolbox.register_tool(self.agency.create_task_tool())
        self.toolbox.register_tool(self.agency.complete_task_tool())

    def start(self):
        self.running = True
        self.thread.start()

    def stop(self):
        self.running = False
        self.thread.join()

    def error(self, message: str):
        self.pubsub.publish("agent_error", message)

    def log(self, message: str):
        self.pubsub.publish("agent_log", message)

    def log_messages(self):
        json_messages = json.dumps([message.to_json() for message in self.messages])
        self.pubsub.publish("agent_log", json_messages)

    def run(self):
        while self.running:
            if self.should_iterate():
                self.log_messages()
                self.iteration += 1
                if self.verbose:
                    self.log(f"Iteration {self.iteration}")
                self.reason()
            time.sleep(1)

    def should_iterate(self):
        if len(self.environment.get_unseen_messages()):
            if self.verbose:
                self.log("Creating messages task.")
            self.agency.create_task(
                description="Review new user messages",
                requirements=[
                    "Review new user messages.",
                    "If need be, create a new task.",
                ],
                completed=False,
            )

        should = self.agency.has_incomplete_tasks()
        if self.verbose:
            self.log(f"Should iterate: {should}")
        return should

    def send_message(self, message: str):
        self.pubsub.publish("new_agent_message", message)

    def reason(self):
        """
        This is where the agent will reason about the environment.
        """
        self.messages.append(
            Message(
                role="user",
                content=self.build_prompt(),
                tool_calls=None,
            )
        )

        response_message = self.llm.get_response(
            self.messages, self.toolbox.get_tools_listed()
        )

        self.messages.append(response_message)

        if self.verbose:
            self.log(f"Response message: {response_message}\n")
        self.act(response_message)

    def act(self, message: Message):
        """
        This is where the agent will act based on the message.
        """

        if message.content:
            return self.send_message(message.content)

        if not message.tool_calls:
            return self.error("No tool calls or message provided.")

        for tool_call in message.tool_calls:
            if self.verbose:
                self.log(
                    f"Running tool: {tool_call.name} with arguments: {tool_call.arguments}"
                )
            else:
                console.print(f"Running tool: {tool_call.name}", style="bold blue")

            returned_message = self.toolbox.run_tool(
                tool_call.name, tool_call.arguments
            )
            self.messages.append(
                Message(
                    content=returned_message,
                    role="tool",
                    tool_call_id=tool_call.id,
                    tool_calls=None,
                )
            )
            self.log(returned_message)

    def percieve(self):
        """
        This is where the perception of the environment will be generated.
        """
        return self.environment.get_environment()

    def remember(self):
        """
        This is where the memory of the agent will be queried.
        """
        if len(self.messages) == 0 or self.messages[-1].content is None:
            return "Memory is empty."
        return self.memory.search_memory(self.messages[-1].content)

    def get_agency(self):
        """
        This is where the goal of the agent will be formed based on user queries.
        """
        agency = self.agency.get_incomplete_tasks_described()
        return agency

    def build_prompt(self):
        perception = self.percieve()
        memory = self.remember()
        agency = self.get_agency()

        prompt = f"""
        Environment: {perception}\n
        Memory: {memory}\n
        Task List: {agency}\n
        """

        return prompt
