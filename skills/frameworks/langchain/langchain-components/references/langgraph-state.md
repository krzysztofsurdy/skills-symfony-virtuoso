# LangGraph State Management and Persistence

## Overview

LangGraph provides comprehensive state management through checkpointers (short-term memory), stores (long-term memory), durable execution, and human-in-the-loop interrupts. These features enable agents to maintain context across interactions, persist through failures, and pause for human intervention.

## Installation

```bash
pip install -U langgraph
# For production persistence:
pip install langgraph-checkpoint-postgres
# or
pip install langgraph-checkpoint-sqlite
```

## Short-Term Memory (Thread-Level Persistence)

Short-term memory enables agents to track multi-turn conversations within a thread.

### Basic Setup with InMemorySaver

```python
from langgraph.checkpoint.memory import InMemorySaver

checkpointer = InMemorySaver()
graph = builder.compile(checkpointer=checkpointer)
graph.invoke(
    {"messages": [{"role": "user", "content": "hello"}]},
    {"configurable": {"thread_id": "1"}}
)
```

### Production Database Checkpointers

#### PostgreSQL

```python
from langgraph.checkpoint.postgres import PostgresSaver

DB_URI = "postgresql://postgres:postgres@localhost:5442/postgres?sslmode=disable"
with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
    graph = builder.compile(checkpointer=checkpointer)
```

#### MongoDB

```python
from langgraph.checkpoint.mongodb import MongoDBSaver

with MongoDBSaver.from_conn_string("mongodb://localhost:27017") as checkpointer:
    graph = builder.compile(checkpointer=checkpointer)
```

#### Redis

```python
from langgraph.checkpoint.redis import RedisSaver

with RedisSaver.from_conn_string("redis://localhost:6379") as checkpointer:
    graph = builder.compile(checkpointer=checkpointer)
```

### Checkpointer Libraries

| Library | Class | Use Case |
|---------|-------|----------|
| `langgraph-checkpoint` | `InMemorySaver` | Development/testing |
| `langgraph-checkpoint-sqlite` | `SqliteSaver` / `AsyncSqliteSaver` | Local development |
| `langgraph-checkpoint-postgres` | `PostgresSaver` / `AsyncPostgresSaver` | Production |
| `langgraph-checkpoint-cosmosdb` | `CosmosDBSaver` / `AsyncCosmosDBSaver` | Azure |

All conform to `BaseCheckpointSaver` interface with methods: `.put()`, `.put_writes()`, `.get_tuple()`, `.list()`.

### Subgraph Integration

Checkpointers automatically propagate to child subgraphs when applied to parent graphs.

## Long-Term Memory (Cross-Thread Store)

Long-term memory shares information across threads using the `Store` interface.

### Basic Setup

```python
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()
graph = builder.compile(checkpointer=checkpointer, store=store)
```

### Store Operations

```python
# Put memory
namespace = ("user_123", "memories")
memory_id = str(uuid.uuid4())
store.put(namespace, memory_id, {"food_preference": "I like pizza"})

# Search memories
memories = store.search(namespace)
memories[-1].dict()  # Returns Item with value, key, namespace, timestamps
```

### Semantic Search

```python
from langchain.embeddings import init_embeddings

store = InMemoryStore(
    index={
        "embed": init_embeddings("openai:text-embedding-3-small"),
        "dims": 1536,
        "fields": ["food_preference", "$"]
    }
)

memories = store.search(
    ("user_123", "memories"),
    query="What does the user like to eat?",
    limit=3
)
```

### Accessing Store in Nodes

The recommended way is through the `Runtime` object:

```python
from langgraph.runtime import Runtime

async def call_model(state: MessagesState, runtime: Runtime[Context]):
    user_id = runtime.context.user_id
    namespace = (user_id, "memories")

    # Search memories
    memories = await runtime.store.asearch(
        namespace,
        query=state["messages"][-1].content,
        limit=3
    )

    # Save memory
    await runtime.store.aput(
        namespace,
        str(uuid.uuid4()),
        {"data": "some memory"}
    )
```

## Checkpoint Management

### View Current State

```python
config = {"configurable": {"thread_id": "1"}}
graph.get_state(config)
```

### View Specific Checkpoint

```python
config = {
    "configurable": {
        "thread_id": "1",
        "checkpoint_id": "1ef663ba-28fe-6528-8002-5a559208592c"
    }
}
graph.get_state(config)
```

### View State History

```python
config = {"configurable": {"thread_id": "1"}}
list(graph.get_state_history(config))  # Most recent first
```

### Update State

Updates respect reducer functions defined on channels:

```python
graph.update_state(config, {"foo": 2, "bar": ["b"]})
```

Optional `as_node` parameter controls which node executes next.

### Replay Execution from Checkpoint

```python
config = {
    "configurable": {
        "thread_id": "1",
        "checkpoint_id": "0c62ca34-ac19-445d-bbb0-5b4984975b2a"
    }
}
graph.invoke(None, config=config)
```

### Delete Checkpoints

```python
checkpointer.delete_thread(thread_id)
```

### Checkpoint Contents

A checkpoint (`StateSnapshot`) contains:
- `config`: Associated configuration
- `metadata`: Checkpoint metadata
- `values`: Current state channel values
- `next`: Node names to execute next
- `tasks`: `PregelTask` objects with execution details and error information

## Message Management Strategies

### Trim Messages

```python
from langchain_core.messages.utils import trim_messages, count_tokens_approximately

messages = trim_messages(
    state["messages"],
    strategy="last",
    token_counter=count_tokens_approximately,
    max_tokens=128
)
```

### Delete Messages

```python
from langchain.messages import RemoveMessage
from langgraph.graph.message import REMOVE_ALL_MESSAGES

def delete_messages(state):
    return {"messages": [RemoveMessage(id=m.id) for m in state["messages"][:2]]}
```

### Summarization

Create running summaries using a model to preserve conversation context while reducing token usage.

## Serialization and Security

### Default Serialization

`JsonPlusSerializer` handles most types. For unsupported types:

```python
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer

graph.compile(
    checkpointer=InMemorySaver(serde=JsonPlusSerializer(pickle_fallback=True))
)
```

### Encryption

```python
from langgraph.checkpoint.serde.encrypted import EncryptedSerializer
from langgraph.checkpoint.sqlite import SqliteSaver

serde = EncryptedSerializer.from_pycryptodome_aes()  # reads LANGGRAPH_AES_KEY
checkpointer = SqliteSaver(sqlite3.connect("checkpoint.db"), serde=serde)
```

## Durable Execution

Durable execution saves workflow progress at key points, allowing pause and resume exactly where left off.

### Core Requirements

1. **Persistence layer** - Checkpointer that preserves workflow progress
2. **Thread identifier** - Track execution history for specific workflow instances
3. **Task wrapping** - Encapsulate non-deterministic and side-effect operations

### Durability Modes

| Mode | Behavior | Trade-off |
|------|----------|-----------|
| `"exit"` | Saves only at completion/interruption | Best performance |
| `"async"` | Async persistence during next step | Balanced |
| `"sync"` | Synchronous saving before next step | Highest durability |

### Determinism on Resume

When resuming, LangGraph identifies an appropriate restart location and replays steps. Key guidelines:
- Wrap side-effect operations (API calls, file writes) in separate tasks
- Encapsulate non-deterministic code (random generation) within tasks or nodes
- Design side effects as idempotent operations

### Resumption Scenarios

```python
# Pause via interrupt
result = graph.invoke(inputs, config)

# Resume after interrupt
graph.invoke(Command(resume=value), config)

# Recovery from failure (re-execute with same thread_id)
graph.invoke(None, config)
```

## Interrupts (Human-in-the-Loop)

Interrupts pause graph execution at specific points for human intervention.

### How Interrupts Work

1. Call `interrupt()` with JSON-serializable value
2. Graph state gets checkpointed automatically
3. Return value surfaces under `__interrupt__` field
4. Resume using `Command(resume=value)` with matching `thread_id`
5. Resumed value becomes the return of the `interrupt()` call

### Requirements

- A checkpointer for state persistence
- A `thread_id` in config
- JSON-serializable payload

### Basic Usage

```python
from langgraph.types import interrupt, Command

def approval_node(state: State):
    approved = interrupt("Do you approve this action?")
    return {"approved": approved}

# Initial invocation
config = {"configurable": {"thread_id": "thread-1"}}
result = graph.invoke({"input": "data"}, config=config)

# Check interrupt payload
print(result["__interrupt__"])

# Resume with response
graph.invoke(Command(resume=True), config=config)
```

### Approval Workflows

```python
def approval_node(state: ApprovalState) -> Command[Literal["proceed", "cancel"]]:
    decision = interrupt({
        "question": "Approve this action?",
        "details": state["action_details"],
    })
    return Command(goto="proceed" if decision else "cancel")
```

### Review and Edit State

```python
def review_node(state: State):
    edited_content = interrupt({
        "instruction": "Review and edit this content",
        "content": state["generated_text"]
    })
    return {"generated_text": edited_content}
```

### Tool Call Interrupts

```python
@tool
def send_email(to: str, subject: str, body: str):
    response = interrupt({
        "action": "send_email",
        "to": to,
        "subject": subject,
        "body": body,
        "message": "Approve sending this email?"
    })
    if response.get("action") == "approve":
        return f"Email sent to {response.get('to', to)}"
    return "Email cancelled by user"
```

### Input Validation Loop

```python
def get_age_node(state: State):
    prompt = "What is your age?"
    while True:
        answer = interrupt(prompt)
        if isinstance(answer, int) and answer > 0:
            break
        prompt = f"'{answer}' is not valid. Enter a positive number."
    return {"age": answer}
```

### Multiple Simultaneous Interrupts

```python
resume_map = {
    i.id: f"answer for {i.value}"
    for i in interrupted_result["__interrupt__"]
}
result = graph.invoke(Command(resume=resume_map), config=config)
```

### Streaming with Interrupts

```python
async for metadata, mode, chunk in graph.astream(
    initial_input,
    stream_mode=["messages", "updates"],
    subgraphs=True,
    config=config
):
    if mode == "updates" and "__interrupt__" in chunk:
        interrupt_info = chunk["__interrupt__"][0].value
        user_response = get_user_input(interrupt_info)
        initial_input = Command(resume=user_response)
        break
```

### Static Breakpoints (Debugging)

```python
# At compile time
graph = builder.compile(
    interrupt_before=["node_a"],
    interrupt_after=["node_b", "node_c"],
    checkpointer=checkpointer,
)

# At runtime
graph.invoke(
    inputs,
    interrupt_before=["node_a"],
    interrupt_after=["node_b"],
    config=config,
)

# Resume
graph.invoke(None, config=config)
```

### Critical Interrupt Rules

**Do NOT wrap in try/except:**
```python
# BAD - bare except catches interrupt exception
try:
    interrupt("What's your name?")
except Exception as e:
    print(e)

# GOOD - use specific exceptions
interrupt("What's your name?")
try:
    fetch_data()
except NetworkException as e:
    print(e)
```

**Maintain consistent interrupt order** (matching is index-based):
```python
# GOOD - same order every execution
name = interrupt("What's your name?")
age = interrupt("What's your age?")

# BAD - conditional interrupts change ordering
name = interrupt("What's your name?")
if state.get("needs_age"):
    age = interrupt("What's your age?")
```

**Ensure idempotent pre-interrupt operations** (code before interrupt re-executes on resume):
```python
# GOOD - idempotent upsert
db.upsert_user(user_id=state["user_id"], status="pending")
approved = interrupt("Approve?")

# GOOD - side effects after interrupt
approved = interrupt("Approve?")
if approved:
    db.create_audit_log(user_id=state["user_id"], action="approved")

# BAD - non-idempotent create before interrupt
audit_id = db.create_audit_log({"user_id": state["user_id"]})  # Duplicates!
approved = interrupt("Approve?")
```

**Only pass JSON-serializable values:**
```python
# GOOD
interrupt("What's your name?")
interrupt({"question": "Details?", "fields": ["name", "email"]})

# BAD
interrupt({"validator": validate_input})      # Cannot serialize
interrupt({"processor": DataProcessor()})     # Cannot serialize
```

**Node re-execution on resume:**
The entire node re-executes from the beginning, not from the interrupt line.

## Database Migration

Most database-specific libraries define a `setup()` method on the checkpointer or store instance. Execute before production deployment or during server startup.

## Key APIs

| API | Purpose |
|-----|---------|
| `InMemorySaver` | Development checkpointer |
| `PostgresSaver` | Production checkpointer |
| `InMemoryStore` | Development long-term store |
| `interrupt()` | Pause for human input |
| `Command(resume=...)` | Resume after interrupt |
| `get_state()` | View current thread state |
| `get_state_history()` | View checkpoint history |
| `update_state()` | Modify graph state |
| `Runtime` | Access store and context in nodes |
| `EncryptedSerializer` | Checkpoint encryption |

## Best Practices

- Use database-backed checkpointers in production (not InMemorySaver)
- Run migrations before deployment
- Implement semantic search for relevant memory retrieval
- Manage context window via trimming, deletion, or summarization
- Pass context at invocation time via `context_schema`
- Design task operations as idempotent
- Wrap side effects in tasks for durable execution
- Use `thread_id` consistently for resume operations
- Only pass JSON-serializable values to interrupts
- Place `interrupt()` calls first in nodes when possible
- Never wrap `interrupt()` in try/except blocks
