#!/usr/bin/env python3

import argparse
import signal
import threading
import time

from rich.console import Console
from rich.markdown import Markdown

from agent.agent import Agent
from llms.openai import OpenAILLM
from tools.toolbox import Toolbox
from utils.pubsub import PubSub

console = Console()

llm_choice = "openai"  # This will be modifiable in the future
verbose = False
silence_actions = False
LLM_CHOICE_MAP = {
    "openai": OpenAILLM,
}
LLM = LLM_CHOICE_MAP[llm_choice]
PUBSUB = PubSub()
TOOLBOX = Toolbox(PUBSUB)


def clear_logs():
    with open("agent.log", "w") as f:
        f.write("")


def clear_threads():
    with open("agent.thread", "w") as f:
        f.write("")


def handle_errors():
    PUBSUB.subscribe("error", lambda error: console.print(f"[red]Error:[/red] {error}"))
    PUBSUB.subscribe(
        "agent_error", lambda error: console.print(f"[red]Agent Error:[/red] {error}")
    )


def write_to_agent_log_file(log: str):
    with open("agent.log", "a") as f:
        current_timestring = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        f.write(f"{current_timestring}: {log}\n")


def write_to_general_log_file(log: str):
    with open("general.log", "a") as f:
        current_timestring = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        f.write(f"{current_timestring}: {log}\n")


def write_to_agent_thread_file(log: str):
    with open("agent.thread", "a") as f:
        current_timestring = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        f.write(f"{current_timestring}: {log}\n")


def handle_logs():
    def agent_log(log: str):
        write_to_agent_log_file(log)

    def general_log(log: str):
        write_to_general_log_file(log)

    PUBSUB.subscribe("agent_log", agent_log)
    PUBSUB.subscribe("general_log", general_log)


def prompt_user():
    user_input = console.input("[cyan bold]You:[/cyan bold] ")
    if user_input.lower() == "exit":
        console.print("[blue bold]Simmy:[/blue bold] Goodbye!")
        PUBSUB.publish("exit_signal", "User exit")
    write_to_agent_thread_file(f"User: {user_input}")
    PUBSUB.publish("new_user_message", user_input)


def on_new_agent_message(message: str):
    console.print("[blue bold]Simmy:[/blue bold]")
    console.print(Markdown(message))
    write_to_agent_thread_file(f"Agent: {message}")
    prompt_user()


def handle_exit(m: str):
    print("Shutting down agent...")
    agent.stop()
    print("Agent stopped. Exiting now.")
    exit(0)


def signal_handler(sig, frame):
    print("\nReceived exit signal, shutting down...")
    PUBSUB.publish("exit_signal", "Signal exit")


PUBSUB.subscribe("new_agent_message", on_new_agent_message)
PUBSUB.subscribe("exit_signal", handle_exit)

if __name__ == "__main__":
    LLM.startup()

    parser = argparse.ArgumentParser(description="Run the Simmy chatbot.")
    parser.add_argument("--llm", type=str, default="openai", help="The LLM to use.")
    parser.add_argument(
        "--verbose", action="store_true", help="Enable verbose logging."
    )
    parser.add_argument(
        "--silence-actions", action="store_true", help="Silence the actions."
    )
    parser.add_argument("--clear-logs", action="store_true", help="Clear the logs.")
    args = parser.parse_args()

    llm_choice = args.llm
    verbose = args.verbose
    silence_actions = args.silence_actions

    if args.clear_logs:
        clear_logs()
    clear_threads()

    console.print("[blue bold]Simmy:[/blue bold] Hello and welcome! My name is Simmy!")

    # Start handling errors and logs in separate threads
    error_thread = threading.Thread(target=handle_errors)
    error_thread.start()

    log_thread = threading.Thread(target=handle_logs)
    log_thread.start()

    # Create and start the agent
    agent = Agent(PUBSUB, LLM, TOOLBOX, verbose, silence_actions)
    agent.start()

    # Set up the signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)

    # Start the interaction loop
    prompt_user()

    # Wait for the agent thread to finish before exiting
    agent.thread.join()
    print("Shutting down...")
