# Memory
Currently, Simple Agent supports memory in a rudimentary form. Essentially, if a Vector Store is specified that the agent can interact with, then it will be capable of creating memories, and recalling them later. The performance of this memory will be enhanced over time.

> [!note]
> Make sure to get Simple Agent working without memory first, by following the instructions in the [Readme](https://github.com/AidanTilgner/Simple-Agent).

# Understanding Vector Stores

> [!note]
> The only vector store currently supported by default is [Simple Vector Store](https://github.com/AidanTilgner/Simple-Vector-Store).

The heart of memories is the `VectorStore` class (`/memory/vector_store.py`), which allows polymorphic interaction with a vector store. If you can adapt to the `VectorStore` class, you can theoretically integrate any model or system you want. The key interface of the `VectorStore` class is as follows:

```python
class VectorStore:
    name: str
    query_store: Callable[[str], List[Record]]
    add_record: Callable[[Record], None]
    on_startup: Callable[[], None]
```

- `name`: The name of the vector store, does not necessarily need to be unique
- `query_store`: This method will be called with a query string, and should return a list of `Record` objects that match the query
- `add_record`: This method will be called with a `Record` object, and should add it to the vector store
- `on_startup`: This method will be called when the agent starts up, and can be used to initialize the vector store

Each `Record` needs to look like this:
```python
class Record:
    id: Optional[int]
    title: str
    content: str
    type: str
    similarity: Optional[float]
    importance: Literal["low", "medium", "high", "extreme"]
```

By adapting to these interfaces, any semantic search integration could theoretically be setup. For a concrete example of setting up a `VectorStore` instance, check out how Simple Vector Store is integrated in the `/memory/simple_vector_store.py` file.

Once you have an instance of a `VectorStore` that you'd like to use, don't forget to go to `simple-agent.py`, and add it to the `VECTOR_STORE_CHOICE_MAP` map as an option. Then, you can set the `VECTOR_STORE_CHOICE` environment variable in your `.env` file to select it.


# Setting Up Memory
Once you've gotten your `VectorStore` of choice selected, don't forget to specify environment variables to make sure that everything is working properly. Relevant environment variables to include in your `.env` are as follows:

```bash
VECTOR_STORE_CHOICE="none" # current options: blank (""), "none", or "simple_vector_store"jkjjjk
```

The defaults here should be fine if you don't want memory. However, if you do, make sure to change these settings to match your desired memory setup.

## Simple Vector Store
Simple Vector Store is a simple choice for memory storage, and allows each memory to be stored simultaneously in a markdown file, as well as vector form. Simple Vector Store currently requires an OpenAI account to function, as it uses the OpenAI API for embeddings generation. There are plans to support other embeddings models for Simple Vector Store, but keep in mind that limitation at the moment.

To start, get set up with Simple Vector Store by following the instructions in the [Simple Vector Store repository](https://github.com/AidanTilgner/Simple-Vector-Store).

Then, fill in the relevant environment variables in your `.env` file:

```bash
# Simple Vector Store Configuration
SIMPLE_VECTOR_STORE_URL="http://localhost:8000" # URL of the Simple Vector Store instance
SIMPLE_VECTOR_STORE_DIRECTORY="/Absolute/Path/to/your/directory/of/choice" # Directory to store simple vector store data, make sure this exists
SIMPLE_VECTOR_STORE_NAME="simple-agent-memory"
```

The most important once to get right here is the `SIMPLE_VECTOR_STORE_DIRECTORY` variable, as this is where all of your memory will be stored. Make sure that this directory exists, and that the agent has read/write permissions to it. Also ensure that it is an absolute path, as relative paths can cause issues.
