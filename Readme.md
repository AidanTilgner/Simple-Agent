# Simple Agent
> [!warning]
> Simple agent can run commands on your machine. Be aware of the potential for it to make modifications to your system.

![simple-agent-run](https://github.com/user-attachments/assets/617e9dab-44e9-4c07-ba67-88fb9a79bb37)

^^ I'll try to have a better demo in the future but this is it working. The file was successfully created here, just FYI.

> [!note]
> Simple Agent is still a work in progress! There will likely be bugs and missing features, if you encounter them, please leave an issue!

This is an attempt to make a bare-bones, very simple agent based on LLMs and other technologies. The goal is to have a simple agent for use in various purposes:

1. Experimentation and benchmarking
2. Understanding and learning myself
3. Idk but having three points sounds more solid

## How it works

So put simply, the agent works on a constant loop, involving three main steps:

1. Perception
2. Inference
3. Action

The perception stage is characterized by a combination of 1. environmental analysis, 2. memory recall, and 3. agency or will towards a goal. The inference stage is the call to the API, where the model (right now only OpenAI models) is given the perception to reason about. The action stage is where the agent takes the output of the model, such as tool calls, and actually runs them.

## How to use it

This repository is a fairly straightforward Python project. **You will need to have Python installed**, and I used Python 3.10 on MacOS, so I know that this version worked. If you use a different version, or use a platform other than MacOS and notice bugs, please let me know in an issue. You should be able to clone the repository, install dependencies (in a virtual environment if you choose), fill in the `.env` file, and run `main.py` to see it work.

1. Start by cloning the repository:

```bash
   git clone https://github.com/AidanTilgner/Simple-Agent.git
````

2. Then, navigate into the directory:
```bash
cd Simple-Agent
````

3a. (Optional) If you choose to use a virtual environment, you can instantiate it like so:

```bash
python -m venv venv
```

Then, activate the virtual environment:

```bash
source ./venv/bin/activate
```

3b. Install the dependencies:

```bash
pip install -r requirements.txt
```

4. Copy the `.env.example` file to `.env` and fill in the necessary information. You will need an OpenAI API key, which you can get from the [OpenAI website](https://platform.openai.com/api-keys).

(on MacOS or Linux):

```bash
cp .env.example .env
```

5. Run the program:

```bash
python main.py
```

6. To exit the program, you can use `Ctrl+C`, or type "exit".

That's it! You should see the agent start up, and you can ask it to do things using it's tools.

## Advanced Usage

You might want to extend or enhance the functionality of the tool, and if you do I'd love to hear how it goes! Or even submit a PR if you think it should be a default.

**Modifying Prompts**
You can modify prompts in the `agent.py`, `agency.py`, `memory.py`, and `environment.py` files. These files are where you'll find the actual programmatic generation logic for several aspects of the prompt. Things might change over time, so I'm not going to go into specifics here. But you might find that you can gain further behavior by modifying these files.

**Using Different Models**
You might find that using different models is more useful. In the future, there will be additional configuration options that will allow you to use models of your choice. For now, you can take a look at the `openai.py` and `llm.py` files for reference. Essentially, the agent can use any model through the `LLM` interface, so you can implement custom models that way. The main logic for instantiating these are in the `main.py` file, where the default is OpenAI's GPT-4o.

**Adding Tools**
The `tools/` directory is where you'll find tools. Each tool must fit the `Tool` class, in order to be used by the agent. Check out `toolbox.py` to see a current list of included tools, and how they are used. If you want to add a tool, you can use the `write_file.py`, `read_file.py`, and `send_message_to_user.py` tools as a reference. More tools will be included in the future. This is another area where PRs are welcome.

## Future plans

These are things that I currently plan on doing. If you have ideas for features or feadback, don't hesitate to open an issue so we can discuss it.

- [ ] Integrate further models or types of LLM
- [ ] Implement memory and learning
- [ ] Add more tools
- [ ] Allow selection of additional models
