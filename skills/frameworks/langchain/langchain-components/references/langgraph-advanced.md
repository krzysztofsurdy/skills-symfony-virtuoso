# LangGraph Advanced Features

## Overview

This reference covers LangGraph's advanced capabilities: subgraphs for modular composition, time travel for debugging, streaming for real-time updates, and application structure for deployment.

## Installation

```bash
pip install -U langgraph
```

## Subgraphs

Subgraphs are graphs used as nodes within other graphs. They enable building multi-agent systems, reusing node sets across graphs, and distributing development across teams.

### Pattern 1: Call Inside a Node Function

Use when parent and subgraph have different state schemas or state transformation is needed:

```python
def call_subgraph(state: ParentState):
    subgraph_output = subgraph.invoke({"bar": state["foo"]})
    return {"foo": subgraph_output["bar"]}

builder.add_node("node_1", call_subgraph)
```

### Pattern 2: Add as Node Directly

Use when parent and subgraph share state keys:

```python
builder.add_node("node_1", subgraph)
```

### Subgraph Persistence Options

| Setting | `checkpointer=False` | `checkpointer=None` (default) | `checkpointer=True` |
|---------|----------------------|-------------------------------|---------------------|
| Interrupts (HITL) | No | Yes | Yes |
| Multi-turn memory | No | No | Yes |
| Different subgraphs | Yes | Yes | Caution |
| Same subgraph multiple times | Yes | Yes | No |
| State inspection | No | Limited | Yes |
| Durable execution | No | Yes | Yes |

#### Stateless Without Interrupts (`checkpointer=False`)

- No durable execution
- Runs like a normal function call
- No checkpointing overhead
- Warning: Cannot recover from crashes mid-run

#### Stateless With Interrupts (`checkpointer=None` - default)

- Recommended for most applications, including multi-agent systems
- Supports `interrupt()` for human-in-the-loop
- Durable execution available
- Each invocation starts fresh (no multi-turn memory)
- Supports parallel tool calls safely

#### Stateful (`checkpointer=True`)

- Subagent remembers previous interactions across calls on same thread
- Each call picks up where the last one left off
- Cannot support parallel tool calls to same subgraph (checkpoint namespace conflicts)

### Namespace Isolation

When multiple different stateful subgraphs exist, wrap each in its own `StateGraph` with unique node names:

```python
# Each subgraph gets a unique namespace
builder_a = StateGraph(StateA)
# ... define nodes ...
subgraph_a = builder_a.compile()

builder_b = StateGraph(StateB)
# ... define nodes ...
subgraph_b = builder_b.compile()

# Add to parent
parent_builder.add_node("agent_a", subgraph_a)
parent_builder.add_node("agent_b", subgraph_b)
```

### State Inspection

```python
subgraph_state = graph.get_state(config, subgraphs=True).tasks[0].state
```

Requirement: Subgraph must be statically discoverable (added directly as node or called within a node function). Does not work when subgraphs are called inside tools.

### Streaming Subgraph Outputs

```python
for chunk in graph.stream({"foo": "foo"}, subgraphs=True, stream_mode="updates"):
    print(chunk)
```

Output includes namespace tuples showing graph hierarchy.

### Multi-Level Subgraphs

Nested hierarchies (parent -> child -> grandchild) use node wrapper functions for different state schemas. Each level transforms state before invoking the next.

### Key Constraints

- Parent graph requires a checkpointer for subgraph persistence features
- Stateful subgraphs don't support parallel tool calls to the same instance
- State inspection requires static discovery of subgraph structure

## Time Travel

Time travel enables examining decision-making processes by resuming execution from prior checkpoints while optionally modifying state.

### Use Cases

- **Understanding reasoning**: Analyzing steps leading to successful outcomes
- **Debugging mistakes**: Identifying error sources
- **Exploring alternatives**: Testing different execution paths

### Workflow

#### 1. Execute Graph

```python
from langgraph.checkpoint.memory import InMemorySaver

checkpointer = InMemorySaver()
graph = builder.compile(checkpointer=checkpointer)

config = {"configurable": {"thread_id": "1"}}
result = graph.invoke({"topic": "dogs"}, config=config)
```

#### 2. Identify Checkpoint

```python
# Retrieve execution history (most recent first)
all_states = list(graph.get_state_history(config))

# Find checkpoint of interest
target_state = all_states[2]  # Example: third checkpoint
target_config = target_state.config
```

#### 3. Modify State (Optional)

```python
# Create new checkpoint with modified state
graph.update_state(target_config, {"topic": "chickens"})
```

#### 4. Resume Execution

```python
# Resume from specific checkpoint
config_with_checkpoint = {
    "configurable": {
        "thread_id": "1",
        "checkpoint_id": "0c62ca34-ac19-445d-bbb0-5b4984975b2a"
    }
}
result = graph.invoke(None, config=config_with_checkpoint)
```

### Key APIs

| Method | Purpose |
|--------|---------|
| `get_state_history(config)` | Retrieve all checkpoints for a thread |
| `update_state(config, values)` | Create new checkpoint with modified state |
| `invoke(None, config)` | Resume from checkpoint |
| `get_state(config)` | Get current state snapshot |

## Streaming

Streaming is crucial for responsive LLM applications, displaying output progressively before complete responses are ready.

### Stream Modes

| Mode | Purpose | Output |
|------|---------|--------|
| `values` | Full state after each step | Complete state dict |
| `updates` | State changes per step | Node name with changes |
| `custom` | User-defined data from nodes | Custom data |
| `messages` | LLM tokens with metadata | 2-tuples (chunk, metadata) |
| `debug` | Comprehensive execution info | Detailed debug data |

### Basic Usage

```python
# Sync
for chunk in graph.stream(inputs, stream_mode="updates"):
    print(chunk)

# Async
async for chunk in graph.astream(inputs, stream_mode="updates"):
    print(chunk)
```

### Graph State Streaming

**Updates mode** returns node names with state modifications:

```python
for chunk in graph.stream({"topic": "ice cream"}, stream_mode="updates"):
    print(chunk)
# Output: {'refineTopic': {'topic': 'ice cream and cats'}}
```

**Values mode** returns complete state snapshots after each step.

### Subgraph Streaming

```python
for chunk in graph.stream({"foo": "foo"}, subgraphs=True, stream_mode="updates"):
    print(chunk)
# Output includes namespace tuples: (namespace_tuple, data)
```

### LLM Token Streaming

The `messages` mode returns tuples of `(message_chunk, metadata)`:

```python
for msg, metadata in graph.stream(inputs, stream_mode="messages"):
    print(msg.content, end="", flush=True)
```

#### Filtering by Tags

```python
joke_model = init_chat_model(model="gpt-4.1-mini", tags=['joke'])

async for msg, metadata in graph.astream(inputs, stream_mode="messages"):
    if metadata["tags"] == ["joke"]:
        print(msg.content, end="|", flush=True)
```

#### Filtering by Node

```python
for msg, metadata in graph.stream(inputs, stream_mode="messages"):
    if metadata["langgraph_node"] == "some_node_name":
        print(msg.content)
```

### Custom Data Streaming

#### From Nodes

```python
from langgraph.config import get_stream_writer

def node(state):
    writer = get_stream_writer()
    writer({"custom_key": "Progress update"})
    return {"answer": "data"}
```

#### From Tools

```python
@tool
def query_database(query: str) -> str:
    """Query the database."""
    writer = get_stream_writer()
    writer({"data": "Retrieved 0/100 records", "type": "progress"})
    return "answer"
```

Access with `stream_mode="custom"`.

#### Arbitrary LLM Integration

```python
from langgraph.config import get_stream_writer

def call_arbitrary_model(state):
    writer = get_stream_writer()
    for chunk in your_custom_streaming_client(state["topic"]):
        writer({"custom_llm_chunk": chunk})
    return {"result": "completed"}
```

### Multiple Stream Modes

```python
for mode, chunk in graph.stream(inputs, stream_mode=["updates", "custom"]):
    print(f"{mode}: {chunk}")
```

### Disabling Streaming

```python
model = init_chat_model("claude-sonnet-4-6", streaming=False)
```

### Python < 3.11 Async Considerations

For LLM calls, pass `RunnableConfig` explicitly:

```python
async def call_model(state, config):
    response = await model.ainvoke(
        [{"role": "user", "content": f"Write about {state.topic}"}],
        config,  # Required for streaming context
    )
    return {"joke": response.content}
```

For custom streaming, use `writer` parameter instead of `get_stream_writer()`:

```python
async def generate_joke(state: State, writer: StreamWriter):
    writer({"custom_key": "Streaming custom data"})
    return {"joke": f"About {state['topic']}"}
```

### Debug Mode

```python
for chunk in graph.stream({"topic": "ice cream"}, stream_mode="debug"):
    print(chunk)
```

## Graph API Advanced Usage

### Sequences

```python
builder.add_sequence(["node_a", "node_b", "node_c"])
# equivalent to:
builder.add_edge(START, "node_a")
builder.add_edge("node_a", "node_b")
builder.add_edge("node_b", "node_c")
```

### Parallel Execution

Fan-out/fan-in patterns execute nodes concurrently:

```python
builder.add_edge(START, "node_a")
builder.add_edge(START, "node_b")  # node_a and node_b run in parallel
builder.add_edge("node_a", "node_c")
builder.add_edge("node_b", "node_c")  # node_c waits for both
```

### Deferred Execution

```python
builder.add_node("reduce_node", reduce_func, defer=True)
```

Delays execution until all pending tasks complete. Useful for map-reduce with uneven branch lengths.

### Overwrite Type

Bypass reducers to directly replace state values:

```python
from langgraph.types import Overwrite

def my_node(state: State):
    return {"my_list": Overwrite(["fresh", "list"])}
```

### Input/Output Schema Filtering

```python
class InputState(TypedDict):
    user_input: str

class OutputState(TypedDict):
    result: str

class InternalState(TypedDict):
    user_input: str
    result: str
    intermediate: str

builder = StateGraph(InternalState, input_schema=InputState, output_schema=OutputState)
```

## Functional API Advanced Usage

### Entrypoint Composition

```python
@entrypoint(checkpointer=checkpointer)
def parent_workflow(inputs: dict):
    result = child_workflow(inputs).result()
    return result

@entrypoint()  # Inherits parent checkpointer
def child_workflow(inputs: dict):
    return process(inputs)
```

### Graph Integration

```python
@entrypoint(checkpointer=checkpointer)
def my_workflow(inputs: dict):
    # Call a compiled graph from functional API
    result = compiled_graph.invoke({"messages": inputs["messages"]})
    return result
```

### Error Handling with Retry

```python
from langgraph.types import RetryPolicy

@task(retry=RetryPolicy(retry_on=ConnectionError, max_attempts=3))
def call_api(data: dict) -> dict:
    return requests.post(API_URL, json=data).json()
```

### Resumption After Failure

Checkpointers preserve task results, allowing continuation without recomputing:

```python
@entrypoint(checkpointer=checkpointer)
def workflow(inputs: dict):
    step1 = task_a(inputs).result()   # Cached if already completed
    step2 = task_b(step1).result()    # Resumes from here on failure
    return step2
```

## Application Structure for Deployment

### Required Components

1. `langgraph.json` - Configuration file
2. Graph implementations - Application logic
3. Dependency file - `requirements.txt` or `pyproject.toml`
4. `.env` file (optional) - Environment variables

### Directory Structure

```
my-app/
├── my_agent/
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── tools.py
│   │   ├── nodes.py
│   │   └── state.py
│   ├── __init__.py
│   └── agent.py
├── .env
├── requirements.txt
└── langgraph.json
```

### Configuration File (langgraph.json)

```json
{
  "dependencies": ["langchain_openai", "./your_package"],
  "graphs": {
    "my_agent": "./your_package/your_file.py:agent"
  },
  "env": "./.env"
}
```

**Key sections:**
- `dependencies`: Required packages and local modules
- `graphs`: Maps graph names to file paths and variables (compiled graphs or graph-generating functions)
- `env`: Points to environment variable file
- `dockerfile_lines`: System libraries/binaries (optional)

## Key APIs

| API | Purpose |
|-----|---------|
| `add_node("name", subgraph)` | Add subgraph as node |
| `get_state(config, subgraphs=True)` | Inspect subgraph state |
| `get_state_history(config)` | Retrieve all checkpoints |
| `update_state(config, values)` | Modify state at checkpoint |
| `stream(inputs, stream_mode=...)` | Stream with specified mode |
| `astream(inputs, stream_mode=...)` | Async streaming |
| `get_stream_writer()` | Custom stream writer |
| `add_sequence([...])` | Add sequential node chain |
| `RetryPolicy` | Configure retry behavior |
| `CachePolicy` | Configure result caching |
| `Overwrite` | Bypass state reducers |

## Best Practices

- Use `checkpointer=None` (default) for most subgraph scenarios
- Use `checkpointer=True` only when subagent needs multi-turn memory
- Never use stateful subgraphs with parallel tool calls to same instance
- Wrap each stateful subgraph in unique `StateGraph` for namespace isolation
- Use time travel for debugging non-deterministic LLM behavior
- Stream with `updates` mode for efficiency, `values` for complete state
- Use `get_stream_writer()` for custom progress updates
- Pass `RunnableConfig` explicitly in async LLM calls (Python < 3.11)
- Use `stream_mode=["updates", "custom"]` to combine multiple modes
- Structure applications with `langgraph.json` for LangSmith deployment
- Use `defer=True` for map-reduce patterns with uneven branches
- Filter streams by tags or node names for targeted output
