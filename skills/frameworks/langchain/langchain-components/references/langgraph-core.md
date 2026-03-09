# LangGraph Core

## Overview

LangGraph is a low-level orchestration framework for building stateful agents and workflows. It models agent workflows as graphs using three foundational components: State, Nodes, and Edges. The framework uses message passing inspired by Google's Pregel, processing in discrete "super-steps" where active nodes execute and pass messages to recipients.

LangGraph is trusted by companies like Klarna, Replit, and Elastic. It draws inspiration from Pregel, Apache Beam, and NetworkX designs. You don't need to use LangChain to use LangGraph.

## Installation

```bash
pip install -U langgraph
# or
uv add langgraph
```

## Core Capabilities

1. **Durable execution** - Agents persist through failures and resume from interruption points
2. **Human-in-the-loop** - State inspection and modification at any point
3. **Comprehensive memory** - Both short-term and long-term storage
4. **Debugging support** - LangSmith integration for visualization and tracing
5. **Production deployment** - Scalable infrastructure for stateful workflows

## Two APIs

LangGraph offers two complementary approaches that share the same runtime:

| Aspect | Graph API | Functional API |
|--------|-----------|----------------|
| Control Flow | Explicit graph paradigm | Standard Python constructs |
| State Management | Requires State declaration and reducers | Function-scoped, no explicit declaration |
| Checkpointing | New checkpoint after each superstep | Results saved to existing checkpoint |
| Visualization | Easy graph visualization | Not supported (dynamic runtime graph) |
| Best For | Complex workflows, team environments | Minimal changes to existing code |

## Graph API

### State Definition

State is a shared data structure representing the application's current snapshot. Can be defined using:

- **TypedDict** (primary approach)
- **Dataclass** (for default values)
- **Pydantic BaseModel** (for recursive data validation, lower performance)

```python
from typing import TypedDict, Annotated
from operator import add

class State(TypedDict):
    foo: int
    bar: Annotated[list[str], add]  # Uses reducer to append
```

#### Multiple Schemas Pattern

```python
class InputState(TypedDict):
    user_input: str

class OutputState(TypedDict):
    graph_output: str

class OverallState(TypedDict):
    foo: str
    user_input: str
    graph_output: str

builder = StateGraph(
    OverallState,
    input_schema=InputState,
    output_schema=OutputState
)
```

#### Messages in State

```python
from langgraph.graph.message import add_messages

class GraphState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
```

The `add_messages` reducer handles message ID tracking and enables updates to existing messages while appending new ones. `MessagesState` is a prebuilt state with this setup.

### Reducers

Each state key has an independent reducer function determining how updates apply. Default behavior overwrites values. Using `operator.add` appends to lists:

```python
from operator import add

class State(TypedDict):
    foo: int                            # Overwrites on update
    bar: Annotated[list[str], add]      # Appends on update
```

### Nodes

Nodes are Python functions (sync or async) that encode agent logic. They accept state as input and return updated state.

```python
def plain_node(state: State):
    return state

def node_with_runtime(state: State, runtime: Runtime[Context]):
    print("In node: ", runtime.context.user_id)
    return {"results": f"Hello, {state['input']}!"}

def node_with_config(state: State, config: RunnableConfig):
    print("In node with thread_id: ", config["configurable"]["thread_id"])
    return {"results": f"Hello, {state['input']}!"}

builder.add_node("plain_node", plain_node)
builder.add_node("node_with_runtime", node_with_runtime)
builder.add_node("node_with_config", node_with_config)
```

#### Special Nodes

```python
from langgraph.graph import START, END

graph.add_edge(START, "node_a")   # Entry point
graph.add_edge("node_a", END)     # Terminal node
```

#### Node Caching

```python
from langgraph.cache.memory import InMemoryCache
from langgraph.types import CachePolicy

builder.add_node(
    "expensive_node",
    expensive_node,
    cache_policy=CachePolicy(ttl=3)
)

graph = builder.compile(cache=InMemoryCache())
```

### Edges

#### Normal Edges

```python
graph.add_edge("node_a", "node_b")
```

#### Conditional Edges

```python
graph.add_conditional_edges("node_a", routing_function)

# With mapping
graph.add_conditional_edges(
    "node_a",
    routing_function,
    {True: "node_b", False: "node_c"}
)
```

#### Entry Points

```python
from langgraph.graph import START

graph.add_edge(START, "node_a")                       # Fixed entry
graph.add_conditional_edges(START, routing_function)   # Conditional entry
```

Multiple outgoing edges execute destination nodes in parallel during the next super-step.

### Send API (Map-Reduce)

```python
from langgraph.types import Send

def continue_to_jokes(state: OverallState):
    return [Send("generate_joke", {"subject": s}) for s in state['subjects']]

graph.add_conditional_edges("node_a", continue_to_jokes)
```

### Command

Combines state updates with control flow:

```python
from langgraph.types import Command

def my_node(state: State) -> Command[Literal["my_other_node"]]:
    return Command(
        update={"foo": "bar"},
        goto="my_other_node"
    )
```

**Command parameters:**
- `update`: State changes
- `goto`: Navigate to specific nodes
- `graph`: Target parent graph from subgraphs
- `resume`: Provide value after interrupt

### Graph Compilation

```python
graph = graph_builder.compile(...)
```

Compilation checks structure, sets runtime arguments like checkpointers and breakpoints. Required before execution.

### Runtime Context

```python
from dataclasses import dataclass

@dataclass
class ContextSchema:
    llm_provider: str = "openai"

graph = StateGraph(State, context_schema=ContextSchema)

# Pass context during invocation
graph.invoke(inputs, context={"llm_provider": "anthropic"})

# Access in nodes
def node_a(state: State, runtime: Runtime[ContextSchema]):
    llm = get_llm(runtime.context.llm_provider)
```

### Recursion Limit

Default is 1000 steps (since v1.0.6). Exceeding raises `GraphRecursionError`.

```python
graph.invoke(inputs, config={"recursion_limit": 5})
```

#### RemainingSteps Managed Value

```python
from langgraph.managed import RemainingSteps

class State(TypedDict):
    remaining_steps: RemainingSteps

def reasoning_node(state: State) -> dict:
    remaining = state["remaining_steps"]
    if remaining <= 2:
        return {"messages": ["Approaching limit, wrapping up..."]}
    return {"messages": ["thinking..."]}
```

#### Available Metadata

```python
metadata = config["metadata"]
print(metadata['langgraph_step'])             # Current step
print(metadata['langgraph_node'])             # Current node
print(metadata['langgraph_triggers'])         # What triggered execution
print(metadata['langgraph_path'])             # Execution path
print(metadata['langgraph_checkpoint_ns'])    # Checkpoint namespace
```

### Graph Composition Patterns

**Sequences:** Chain nodes linearly using `add_sequence()` or manual `add_edge()` calls.

**Parallel Execution:** Fan-out/fan-in patterns execute nodes concurrently within supersteps.

**Conditional Branching:** Use `add_conditional_edges()` to route based on state values.

**Deferred Execution:** Set `defer=True` to delay execution until all pending tasks complete (useful for map-reduce with uneven branches).

### Overwrite Type

Bypass reducers to directly replace state values:

```python
from langgraph.types import Overwrite
# or use "__overwrite__" JSON key
```

### Retry Policies

```python
from langgraph.types import RetryPolicy

builder.add_node("my_node", my_node, retry=RetryPolicy(max_attempts=3))
```

### Async Support

```python
async def my_node(state: State):
    result = await some_async_call()
    return {"result": result}

await graph.ainvoke(inputs)
# or
async for chunk in graph.astream(inputs):
    print(chunk)
```

### Visualization

Render graphs as Mermaid diagrams or PNG using Graphviz:

```python
graph.get_graph().draw_mermaid_png()
```

## Functional API

### Entrypoint

The `@entrypoint` decorator marks a function as the workflow starting point:

```python
from langgraph.func import entrypoint, task
from langgraph.checkpoint.memory import InMemorySaver

@entrypoint(checkpointer=InMemorySaver())
def my_workflow(inputs: dict) -> int:
    value = inputs["value"]
    result = my_task(value).result()
    return result
```

#### Injectable Parameters

| Parameter | Purpose |
|-----------|---------|
| `previous` | Access prior checkpoint state for given thread |
| `store` | BaseStore instance for long-term memory |
| `writer` | StreamWriter for async Python < 3.11 |
| `config` | Runtime configuration access |

#### Short-term Memory with `previous`

```python
@entrypoint(checkpointer=checkpointer)
def my_workflow(inputs: dict, *, previous=None) -> int:
    # previous contains return value from prior invocation on same thread
    pass
```

Use `entrypoint.final(value=return_val, save=saved_val)` to decouple returned values from checkpoint-persisted values.

### Tasks

The `@task` decorator marks functions as executable units that return future-like objects:

```python
@task
def add_one(x: int) -> int:
    return x + 1

# Inside an entrypoint
result = add_one(5).result()  # Synchronous
# or
result = await add_one(5)      # Async
```

#### When to Use Tasks

- Checkpointing long-running operations
- Human-in-the-loop workflows (encapsulating randomness)
- Parallel I/O-bound operations
- Observability and monitoring
- Retryable work management

#### Parallel Execution

```python
futures = [add_one(i) for i in numbers]
return [f.result() for f in futures]
```

### Critical Design Patterns

**Serialization:** Both entrypoint inputs/outputs and task outputs must be JSON-serializable.

**Determinism:** Randomness must be encapsulated inside tasks to ensure resumed workflows follow identical execution sequences.

**Idempotency:** Design task operations as idempotent to prevent duplicate API calls on re-execution.

**Side Effects:** Encapsulate side effects (file writes, emails) in tasks to prevent re-execution upon resumption.

### Entrypoint Composition

Entrypoints can call other entrypoints. Child entrypoints automatically inherit parent checkpointers.

### Task Caching

```python
@task(cache_policy=CachePolicy(ttl=120))
def my_task(x: int) -> int:
    return x + 1
```

## Quickstart: Calculator Agent

### Graph API Approach

```python
from langchain_anthropic import ChatAnthropic
from langgraph.graph import StateGraph, MessagesState, START, END

# 1. Define tools
@tool
def multiply(a: int, b: int) -> int:
    """Multiply a and b."""
    return a * b

@tool
def add(a: int, b: int) -> int:
    """Add a and b."""
    return a + b

@tool
def divide(a: int, b: int) -> float:
    """Divide a by b."""
    return a / b

tools = [multiply, add, divide]
tools_by_name = {tool.name: tool for tool in tools}

# 2. Model with tools
model = ChatAnthropic(model="claude-sonnet-4-6")
model_with_tools = model.bind_tools(tools)

# 3. State
class State(MessagesState):
    llm_calls: int

# 4. LLM node
def llm_call(state: State):
    return {
        "messages": [model_with_tools.invoke(
            [{"role": "system", "content": "You are a helpful assistant."}]
            + state["messages"]
        )],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }

# 5. Tool node
def tool_node(state: State):
    result_messages = []
    for tool_call in state["messages"][-1].tool_calls:
        tool = tools_by_name[tool_call["name"]]
        result = tool.invoke(tool_call["args"])
        result_messages.append(
            ToolMessage(content=str(result), tool_call_id=tool_call["id"])
        )
    return {"messages": result_messages}

# 6. Routing
def should_continue(state: State):
    if state["messages"][-1].tool_calls:
        return "tool_node"
    return END

# 7. Build graph
builder = StateGraph(State)
builder.add_node("llm_call", llm_call)
builder.add_node("tool_node", tool_node)
builder.add_edge(START, "llm_call")
builder.add_conditional_edges("llm_call", should_continue)
builder.add_edge("tool_node", "llm_call")
graph = builder.compile()
```

### Functional API Approach

```python
from langgraph.func import entrypoint, task

@task
def call_llm(messages):
    return model_with_tools.invoke(
        [{"role": "system", "content": "You are a helpful assistant."}]
        + messages
    )

@task
def call_tool(tool_call):
    tool = tools_by_name[tool_call["name"]]
    result = tool.invoke(tool_call["args"])
    return ToolMessage(content=str(result), tool_call_id=tool_call["id"])

@entrypoint()
def agent(messages):
    llm_calls = 0
    while True:
        response = call_llm(messages).result()
        messages = messages + [response]
        llm_calls += 1
        if not response.tool_calls:
            break
        tool_results = [call_tool(tc).result() for tc in response.tool_calls]
        messages = messages + tool_results
    return {"messages": messages, "llm_calls": llm_calls}
```

## Workflows and Agents

### Workflow Patterns

| Pattern | Description | Use Case |
|---------|-------------|----------|
| Prompt Chaining | Sequential LLM calls processing previous output | Document translation, content verification |
| Parallelization | LLMs work simultaneously on tasks | Speed, confidence validation |
| Routing | Direct inputs to context-specific tasks | Different content types |
| Orchestrator-Worker | Orchestrator breaks tasks, workers execute | Complex multi-part tasks |
| Evaluator-Optimizer | One LLM generates, another evaluates | Translation refinement |

### Agents

Agents operate in continuous feedback loops for unpredictable problems:

```python
@tool
def multiply(a: int, b: int) -> int:
    """Multiply a and b."""
    return a * b
```

Agents receive tool definitions and autonomously decide which to invoke based on goals.

## Thinking in LangGraph

### Five-Step Development Process

1. **Map workflow as discrete steps** - Break process into individual nodes and sketch connections
2. **Identify operation types** - LLM steps, Data steps, Action steps, User input steps
3. **Design state structure** - Store raw data, not formatted text. Format prompts inside nodes
4. **Build node functions** - Accept current state and return updates
5. **Wire nodes together** - Minimal graph structure with essential edges

### Error Handling Strategies

| Error Type | Handler | Strategy |
|-----------|---------|----------|
| Transient (network/rate limits) | System | Retry policies |
| LLM-recoverable | LLM | Store error, loop back |
| User-fixable | Human | Use `interrupt()` |
| Unexpected | Developer | Bubble up |

### Node Granularity Trade-offs

Smaller nodes provide:
- Better isolation of external service failures
- Intermediate state visibility for debugging
- Independent retry configuration per operation type
- Improved testability and reusability

## Graph Migrations

LangGraph handles topology changes while preserving checkpointed state:
- Threads at graph end: All changes supported
- Interrupted threads: All changes except renaming/removing interrupted nodes
- State keys: Full backwards/forwards compatibility for adding/removing
- Renamed keys: Lose saved state in existing threads

## Key APIs

| API | Purpose |
|-----|---------|
| `StateGraph` | Build graph with typed state |
| `MessagesState` | Prebuilt state for LLM conversations |
| `START`, `END` | Entry and terminal nodes |
| `Command` | Combined state update + control flow |
| `Send` | Dynamic routing for map-reduce |
| `@entrypoint` | Functional API workflow entry |
| `@task` | Functional API work unit |
| `RetryPolicy` | Configurable retry behavior |
| `CachePolicy` | Node/task result caching |
| `Runtime` | Access context and store in nodes |
| `RunnableConfig` | Thread ID, metadata access |

## Best Practices

- State should store raw data, not formatted text
- Format prompts inside nodes when needed
- Use `Command` objects for routing decisions within nodes
- Call `interrupt()` first in nodes requiring human input
- Design side effects as idempotent operations
- Encapsulate non-deterministic code within tasks or nodes
- Use `RetryPolicy` for transient failures
- Compile with `MemorySaver` checkpointer for persistence
- Use `thread_id` for resumable execution
