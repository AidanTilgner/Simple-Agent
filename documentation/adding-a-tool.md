# Adding a Tool
Adding a tool is a relatively straightforward process in Simple Agent, however there are some key concepts that are useful to understand.

## Tools Library
All of the tools are defined under the `tools/libraries/` directory in the root of the project. The only library present by default is the `core/` library, which is a directory under `tools/libraries/` that contains all of the core tools that are used by the system. You can add new libraries by creating a new directory under `tools/libraries/` and adding tools to it. These can later be imported and used in `Roles`, which will be explained later.

> [!note]
> For information on Roles specifically, check out the [Adding a Role](./adding-a-role.md) guide.

If you're looking to add tools, I'd recommend adding a new library to the `tools/libraries/` directory, and then making a new file for each tool you'd like to add. This will help keep your tools organized and easy to find. With that said, let's get started!

## Tool Configuration
Simple Agent tools all follow a common pattern, and ultimately must adapt to the `Tool` class, which you'll find in `tools/index.py`. The tool class looks like this:
```python
@dataclass
class Tool:
    name: str
    description: str
    function: Callable[
        [PubSub, Any], (str)
    ]
    parameters: Dict[str, Any]
```

So a `Tool` must have a `name`, a `description`, a `function`, and `parameters` to be properly utilized by the system. The `name` and `description` are self-explanatory. We'll get to the function part. However, the `parameters` are used to define how the function should be called, and should follow the [JSON Schema](https://json-schema.org/) specification. The JSON Schema specification is a way to define the arguments that should be passed to a function, and so this is where you define what variables you need passed to your tool.

For example, the `write_file` tool's definition looks like this:
```python
write_file = Tool(
    name="write_file",
    description="Write to a file",
    function=run,
    parameters={
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "The path to the file to read.",
            },
            "content": {
                "type": "string",
                "description": "The content to write to the file.",
            },
            "mode": {
                "type": "string",
                "enum": ["w", "a", "x"],
                "description": "The mode to open the file in. Defaults to 'w'.",
            },
        },
        "required": ["file_path", "content", "mode"],
    },
)
```

The `write_file` tool takes a `file_path`, `content`, and `mode` as arguments. The `file_path` is the path to the file to write to, the `content` is the content to write to the file, and the `mode` is the mode to open the file in. The `mode` is an enum, meaning it can only be one of the values in the list `["w", "a", "x"]`. The `required` field is a list of the arguments that are required to be passed to the function.

> [!note]
> This is a system which relies heavily on natural language, so it's important to describe your tool well, as it becomes part of the language model's prompt.

As far as the `function` goes, this is what actually runs when the agent calls your tool. Going back to the `write_file` tool, the `run` function is defined as follows:

```python
def run(args: Any):
    if not args:
        return "Error running send_message_to_user: No message provided."
    try:
        contents = args.get("content")
        with open(args["file_path"], "w") as file:
            file.write(contents)
        with open(args["file_path"], "r") as file:
            content = file.read()
            return f"New file content: \n{content}"

        return "File not read."
    except Exception as e:
        return f"Error writing to file: {e}"
```

There are a couple of things to note here.

First, **the function always returns a string**. This is important because this string will actually be passed to the model, and therefore should give context as to the results of the tool.

Second, due to the technically unpredictable nature of the `args` passed, each tool should check to make sure that the arguments are present before trying to use them. This is why the `run` function checks to make sure that `args` is not `None` before trying to use it.

I also want to mention, that a second argument is passed to all tools, which is the `PubSub` object. This object is used to publish messages to the user, and is used in the `send_message_to_user` tool, for example:

```python
def run(args: Any, ps: PubSub):
    if not args:
        return "Error running send_message_to_user: No message provided."
    ps.publish("new_agent_message", args.get("content"))
    return "Message sent to user."
```

You may choose to use this object in your tools, or you may not. It's up to you. If you choose not to use it, you may simply omit it from the function argument.

## Adding to a Role

> [!note]
> For information on Roles specifically, check out the [Adding a Role](./adding-a-role.md) guide.

Roles are defined in the `roles/` directory. By default, you'll find the core roles under the `core/` directory. To add a tool to a role, you'll need to first locate its definition. For example, the `Developer` role is located in `roles/core/developer.py`. In this file, you'll find the `Developer` role defined as follows:

```python
from roles.index import Role
from tools.libraries.core.web_request import web_request
# ...other imports...
from tools.libraries.core.read_file import read_file

TOOLS = [web_request, write_file, run_js, edit_file, exec_command, read_file]

DEVELOPER = Role(
    name="Developer",
    identity="""
    A dedicated developer with tools for developing software, building applications, managing projects, and debugging.
    """,
    tools=TOOLS,
)
```

The agent only has access to the tools that are defined under the role that it's currently adopted. The Developer role would need to be adopted before these tools are all available. You can also overlap tools between roles, as some tools may be used by multiple roles. With that said, a role's tools are simply defined as a list of `Tool` objects, so to add a new tool to a role, you would simply add it to the list of tools in the role's definition.

## Quick Example
For now, we'll just use the example of an `echo` tool, which when called, will echo what is passed to it as a message.

In the `tools/libraries/` directory, create a new directory called `custom/`.

In the `tools/libraries/custom/` directory, create a new file called `echo.py`.

Within this `echo.py` file, we're going to configure the `echo` tool. We'll start with the `run` function, which we will define as follows:

```python
def run(args: Any):
    if not args.get("message"):
        return "Error running echo: No message provided."
    print(args.get("message"))
    return args.get("message")
```

Now that we've configured the function itself, we need to define the `Tool` object. This will look like this:

```python
echo = Tool(
    name="echo",
    description="Echo a message",
    function=run,
    parameters={
        "type": "object",
        "properties": {
            "message": {
                "type": "string",
                "description": "The message to echo.",
            },
        },
        "required": ["message"],
    },
)
```

Now that we've defined the `echo` tool, we need to add it to a role. For this example, we'll add it to the `Developer` role. Open the `roles/core/developer.py` file and add the `echo` tool to the `TOOLS` list:

```python
from roles.index import Role
from tools.libraries.custom.echo import echo
# ...other imports...
from tools.libraries.core.read_file import read_file

TOOLS = [web_request, write_file, run_js, edit_file, exec_command, read_file, echo]

DEVELOPER = Role(
    name="Developer",
    identity="""
    A dedicated developer with tools for developing software, building applications, managing projects, and debugging.
    """,
    tools=TOOLS,
)
```

Now, when the `Developer` role is adopted, the `echo` tool will be available to the agent.
