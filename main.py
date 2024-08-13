import threading
import time

from agent.agent import Agent
from llms.openai import OpenAILLM
from tools.toolbox import Toolbox
from utils.pubsub import PubSub

LLM_CHOICE = "openai"
LLM_CHOICE_MAP = {
    "openai": OpenAILLM,
}

LLM = LLM_CHOICE_MAP[LLM_CHOICE]
PUBSUB = PubSub()
TOOLBOX = Toolbox(PUBSUB)


def handle_errors():
    PUBSUB.subscribe("error", lambda error: print(f"Error: {error}"))
    PUBSUB.subscribe("agent_error", lambda error: print(f"Agent Error: {error}"))


def write_to_agent_log_file(log: str):
    with open("agent.log", "a") as f:
        current_timestring = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        f.write(f"{current_timestring}: {log}\n")


def write_to_agent_thread_file(log: str):
    with open(".agent_thread", "a") as f:
        current_timestring = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        f.write(f"{current_timestring}: {log}\n")


def handle_logs():
    PUBSUB.subscribe("log", lambda log: print(f"Log: {log}"))
    PUBSUB.subscribe("agent_log", lambda log: print(f"Agent Log: {log}"))


def start_chat():
    def on_new_agent_message(message: str):
        print(f"Chatbot: {message}")
        write_to_agent_thread_file(f"Agent: {message}")

    PUBSUB.subscribe("new_agent_message", on_new_agent_message)

    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Chatbot: Goodbye!")
            break
        PUBSUB.publish("new_user_message", user_input)
        write_to_agent_thread_file(f"User: {user_input}")


if __name__ == "__main__":
    print("""
Hello and welcome to Simple Agent!
    """)
    handle_errors()
    handle_logs()

    print("Initializing agent...")
    agent = Agent(PUBSUB, LLM, TOOLBOX)
    print("Running agent...")
    agent.start()

    chat_thread = threading.Thread(target=start_chat)
    chat_thread.start()

    chat_thread.join()
    agent.stop()

    start_chat()
    print("Shutting down...")
