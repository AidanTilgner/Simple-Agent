import json
import threading
import time
from typing import List

from agent.agency import Agency
from agent.environment import Environment
from agent.memory import Memory
from llms.llm import LLM, Message
from tools.toolbox import Toolbox
from utils.pubsub import PubSub


class Agent:
    pubsub: PubSub
    messages: List[Message] = []
    llm: LLM
    toolbox: Toolbox
    environment: Environment
    memory: Memory
    agency: Agency
    running: bool = False
    thread: threading.Thread

    def __init__(self, pubsub: PubSub, llm: LLM, toolbox: Toolbox) -> None:
        self.pubsub = pubsub
        self.llm = llm
        self.toolbox = toolbox
        self.environment = Environment(pubsub)
        self.memory = Memory(pubsub)
        self.agency = Agency(pubsub, llm)
        self.thread = threading.Thread(target=self.run)

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

    def run(self):
        while self.running:
            if self.environment.new_perception():
                print("Reasoning...")
                self.reason()
            time.sleep(1)

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
        print("Response message:", json.dumps(response_message))
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
            returned_message = self.toolbox.run_tool(
                tool_call.name, tool_call.arguments
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
            return "Blank memory"
        return self.memory.search_memory(self.messages[-1].content)

    def form_goal(self):
        """
        This is where the goal of the agent will be formed based on user queries.
        """
        agency = self.agency.get_agency(self.messages)
        self.log(f"Agency: {agency}")
        return agency

    def build_prompt(self):
        perception = self.percieve()
        memory = self.remember()
        agency = self.form_goal()

        prompt = f"""
        Perception: {perception}\n
        Memory: {memory}\n
        Agency: {agency}\n
        """

        return prompt
