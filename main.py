import argparse
import signal
import time

from agent.agent import Agent
from llms.openai import OpenAILLM
from tools.toolbox import Toolbox
from utils.pubsub import PubSub

llm_choice = "openai"
verbose = False
LLM_CHOICE_MAP = {
    "openai": OpenAILLM,
}

LLM = LLM_CHOICE_MAP[llm_choice]
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
    def agent_log(log: str):
        write_to_agent_log_file(log)
    PUBSUB.subscribe("agent_log", agent_log)


def prompt_user():
    user_input = input("You: ")
    if user_input.lower() == "exit":
        print("SIMMY: Goodbye!")
        PUBSUB.publish("exit_signal", "User exit")
    write_to_agent_thread_file(f"User: {user_input}")
    PUBSUB.publish("new_user_message", user_input)

def on_new_agent_message(message: str):
    print(f"SIMMY: {message}")
    write_to_agent_thread_file(f"Agent: {message}")
    prompt_user()

PUBSUB.subscribe("new_agent_message", on_new_agent_message)
PUBSUB.subscribe("exit_signal", lambda _: agent.stop())

if __name__ == "__main__":
    # init argparse
    parser = argparse.ArgumentParser(description="Run the SIMMY chatbot.")
    parser.add_argument("--llm", type=str, default="openai", help="The LLM to use.")
    parser.add_argument(
        "--verbose", action="store_true", help="Enable verbose logging."
    )
    args = parser.parse_args()

    llm_choice = args.llm
    verbose = args.verbose

    print("Hello and welcome! My name is SIMMY!")
    handle_errors()
    handle_logs()

    agent = Agent(PUBSUB, LLM, TOOLBOX, verbose)
    agent.start()

    signal.signal(signal.SIGTERM, lambda sig, frame: agent.stop())
    signal.signal(signal.SIGINT, lambda sig, frame: agent.stop())

    prompt_user()
    print("Shutting down...")
