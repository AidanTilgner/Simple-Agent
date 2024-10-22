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
from utils.tokens import get_current_num_tokens, truncate_message

console = Console()


class Agent:
    pubsub: PubSub
    messages: List[Message] = []
    llm: LLM
    toolbox: Toolbox
    environment: Environment
    memory: Memory
    agency: Agency
    running: bool = False
    awake: bool = False
    thread: threading.Thread
    verbose: bool
    silence_actions: bool
    iteration: int = 0

    def __init__(
        self,
        pubsub: PubSub,
        llm: LLM,
        toolbox: Toolbox,
        verbose: bool,
        silence_actions: bool,
    ) -> None:
        self.pubsub = pubsub
        self.llm = llm
        self.toolbox = toolbox
        self.verbose = verbose
        self.silence_actions = silence_actions
        self.environment = Environment(pubsub)
        self.memory = Memory(pubsub)
        self.agency = Agency(pubsub, llm=llm, silence_actions=silence_actions)
        self.thread = threading.Thread(target=self.run)

        self.toolbox.register_tool(self.agency.create_task_tool())
        self.toolbox.register_tool(self.agency.complete_task_tool())
        self.toolbox.register_tool(self.agency.modify_task_notes_tool())

    def start(self):
        self.running = True
        self.thread.start()

    def stop(self):
        self.running = False

    def error(self, message: str):
        self.pubsub.publish("agent_error", message)

    def log(self, message: str):
        self.pubsub.publish("agent_log", message)

    def log_messages(self):
        json_messages = json.dumps([message.to_json() for message in self.messages])
        self.pubsub.publish("agent_log", json_messages)

    def run(self):
        if self.running:
            if self.check_waking_state():
                self.log_messages()
                self.iteration += 1
                if self.verbose:
                    self.log(f"Iteration {self.iteration}")
                response_message = self.reason()
                self.act(response_message)
                self.run()

            time.sleep(1)
            self.run()

    def check_waking_state(self):
        if self.agency.has_incomplete_tasks():
            self.awake = True
        else:
            self.awake = False

        if self.environment.new_stimuli():
            self.awake = True

        return self.awake

    def send_message(self, message: str):
        self.pubsub.publish("new_agent_message", message)

    def reason(self):
        """
        This is where the agent will reason about the environment.
        """
        self.messages.append(
            Message(
                id=None,
                role="user",
                content=self.build_prompt(),
                tool_calls=None,
            )
        )

        with console.status("[bold blue]Simmy is thinking...", spinner="dots12"):
            response_message = self.llm.get_response(
                self.messages, self.toolbox.get_tools_listed()
            )
            response_message = truncate_message(response_message)

        self.messages.append(response_message)

        if self.verbose:
            self.log(f"Response message: {response_message}\n")

        return response_message

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
                    f"Running {tool_call.name} with arguments: {tool_call.arguments}"
                )
            if not self.silence_actions:
                console.print(
                    f"[bold]Running[/bold] {tool_call.name}", style="bright_black"
                )

            returned_message = self.toolbox.run_tool(
                tool_call.name, tool_call.arguments
            )
            self.pubsub.publish("new_tool_message", returned_message)
            self.messages.append(
                Message(
                    id=None,
                    content=returned_message,
                    role="tool",
                    tool_call_id=tool_call.id,
                    tool_calls=None,
                )
            )
            self.log(returned_message)
        return True

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

    def check_token_length(self):
        try:
            tokens = get_current_num_tokens(self.messages, self.llm.model_name)
            return tokens
        except Exception as e:
            self.error(f"Error getting token length: {e}")
            return 0
