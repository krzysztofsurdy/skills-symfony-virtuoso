# Retrieval and RAG

## Overview

Retrieval mechanisms address two fundamental LLM limitations: finite context windows and static training knowledge. LangChain provides a complete retrieval pipeline through Retrieval-Augmented Generation (RAG), enabling systems to fetch relevant external knowledge at query time and pass it to the LLM for answer generation.

The retrieval pipeline consists of two phases: **indexing** (loading, splitting, embedding, and storing documents) and **retrieval & generation** (fetching relevant context and generating answers). LangChain supports both agentic RAG (LLM decides when to retrieve) and two-step RAG chains (always retrieve then generate).

## Installation

```bash
pip install langchain langchain-text-splitters langchain-community bs4
```

Additional packages depend on your chosen LLM, embeddings provider, and vector store.

## Retrieval Pipeline Components

| Component | Purpose | Key Class |
|---|---|---|
| Document Loaders | Ingest data from external sources | `WebBaseLoader`, `PyPDFLoader` |
| Text Splitters | Break documents into retrievable chunks | `RecursiveCharacterTextSplitter` |
| Embedding Models | Convert text to numerical vectors | `OpenAIEmbeddings`, `GoogleGenerativeAIEmbeddings` |
| Vector Stores | Store and retrieve embeddings | `InMemoryVectorStore`, `Chroma`, `FAISS`, `Pinecone` |
| Retrievers | Interface returning documents for queries | `VectorStoreRetriever` |

## RAG Architecture Types

| Type | Characteristics | Control | Flexibility | Latency |
|---|---|---|---|---|
| 2-Step RAG | Fixed retrieval-then-generation sequence | High | Low | Predictable |
| Agentic RAG | LLM decides when/how to retrieve | Low | High | Variable |
| Hybrid RAG | Combines both with validation steps | Medium | Medium | Medium |

## Indexing: Document Loading

### Web Content

```python
import bs4
from langchain_community.document_loaders import WebBaseLoader

bs4_strainer = bs4.SoupStrainer(class_=("post-title", "post-header", "post-content"))
loader = WebBaseLoader(
    web_paths=("https://lilianweng.github.io/posts/2023-06-23-agent/",),
    bs_kwargs={"parse_only": bs4_strainer},
)
docs = loader.load()
```

### PDF Content

```python
from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader("example.pdf")
docs = loader.load()
```

Documents have three attributes: `page_content` (text), `metadata` (contextual info), and optional `id`.

## Indexing: Text Splitting

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    add_start_index=True,
)
all_splits = text_splitter.split_documents(docs)
```

| Parameter | Purpose |
|---|---|
| `chunk_size` | Character limit per chunk |
| `chunk_overlap` | Characters repeated between consecutive chunks |
| `add_start_index` | Tracks position in original document |

## Indexing: Embeddings

```python
# OpenAI
from langchain_openai import OpenAIEmbeddings
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

# Google Gemini
from langchain_google_genai import GoogleGenerativeAIEmbeddings
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

# HuggingFace
from langchain_huggingface import HuggingFaceEmbeddings
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

# AWS Bedrock
from langchain_aws import BedrockEmbeddings
embeddings = BedrockEmbeddings(model_id="amazon.titan-embed-text-v2:0")
```

## Indexing: Vector Stores

```python
# Store documents
document_ids = vector_store.add_documents(documents=all_splits)
```

Supported vector stores: InMemoryVectorStore, Chroma, FAISS, Milvus, MongoDB Atlas, PGVector, Pinecone, Qdrant, AstraDB, Amazon OpenSearch, Cohere, Weaviate.

## Retrieval: Agentic RAG (Tool-Based)

The LLM decides when and how to retrieve. Supports multiple sequential searches and skips retrieval for simple queries.

```python
from langchain.tools import tool
from langchain.agents import create_agent

@tool(response_format="content_and_artifact")
def retrieve_context(query: str):
    """Retrieve information to help answer a query."""
    retrieved_docs = vector_store.similarity_search(query, k=2)
    serialized = "\n\n".join(
        (f"Source: {doc.metadata}\nContent: {doc.page_content}")
        for doc in retrieved_docs
    )
    return serialized, retrieved_docs

tools = [retrieve_context]
prompt = (
    "You have access to a tool that retrieves context from a blog post. "
    "Use the tool to help answer user queries."
)
agent = create_agent(model, tools, system_prompt=prompt)

# Execute with streaming
query = "What is the standard method for Task Decomposition?"
for event in agent.stream(
    {"messages": [{"role": "user", "content": query}]},
    stream_mode="values",
):
    event["messages"][-1].pretty_print()
```

The `response_format="content_and_artifact"` decorator attaches raw documents as artifacts separate from the stringified text sent to the model.

**Trade-offs:** Two inference calls when searching (one for query generation, one for response), but less unnecessary retrieval.

## Retrieval: Two-Step RAG Chain

Always performs retrieval with a single LLM call. Lower latency, guaranteed context injection.

```python
from langchain.agents.middleware import dynamic_prompt, ModelRequest

@dynamic_prompt
def prompt_with_context(request: ModelRequest) -> str:
    """Inject context into state messages."""
    last_query = request.state["messages"][-1].text
    retrieved_docs = vector_store.similarity_search(last_query)

    docs_content = "\n\n".join(doc.page_content for doc in retrieved_docs)

    system_message = (
        "You are a helpful assistant. Use the following context in your response:"
        f"\n\n{docs_content}"
    )
    return system_message

agent = create_agent(model, tools=[], middleware=[prompt_with_context])
```

### Including Source Documents in Two-Step Chains

```python
from typing import Any
from langchain_core.documents import Document
from langchain.agents.middleware import AgentMiddleware, AgentState

class State(AgentState):
    context: list[Document]

class RetrieveDocumentsMiddleware(AgentMiddleware[State]):
    state_schema = State

    def before_model(self, state: AgentState) -> dict[str, Any] | None:
        last_message = state["messages"][-1]
        retrieved_docs = vector_store.similarity_search(last_message.text)
        docs_content = "\n\n".join(doc.page_content for doc in retrieved_docs)
        augmented_message_content = (
            f"{last_message.text}\n\nUse the following context:\n{docs_content}"
        )
        return {
            "messages": [last_message.model_copy(update={"content": augmented_message_content})],
            "context": retrieved_docs,
        }

agent = create_agent(
    model,
    tools=[],
    middleware=[RetrieveDocumentsMiddleware()],
)
```

## Retriever Search Types

| Search Type | Description |
|---|---|
| `similarity` | Default cosine similarity search |
| `mmr` | Maximum marginal relevance - balances relevance with diversity |
| `similarity_score_threshold` | Returns only results above a score threshold |

## Complete Example

```python
import bs4
from langchain.agents import create_agent
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.tools import tool

# Load and chunk content
bs4_strainer = bs4.SoupStrainer(class_=("post-title", "post-header", "post-content"))
loader = WebBaseLoader(
    web_paths=("https://lilianweng.github.io/posts/2023-06-23-agent/",),
    bs_kwargs={"parse_only": bs4_strainer},
)
docs = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
all_splits = text_splitter.split_documents(docs)

# Index chunks
vector_store.add_documents(documents=all_splits)

# Create retrieval tool
@tool(response_format="content_and_artifact")
def retrieve_context(query: str):
    """Retrieve information to help answer a query."""
    retrieved_docs = vector_store.similarity_search(query, k=2)
    serialized = "\n\n".join(
        (f"Source: {doc.metadata}\nContent: {doc.page_content}")
        for doc in retrieved_docs
    )
    return serialized, retrieved_docs

# Build and run agent
tools = [retrieve_context]
prompt = "You have access to a tool that retrieves blog context. Use it to help answer queries."
agent = create_agent(model, tools, system_prompt=prompt)

query = "What is task decomposition?"
for step in agent.stream(
    {"messages": [{"role": "user", "content": query}]},
    stream_mode="values",
):
    step["messages"][-1].pretty_print()
```

## Key APIs

| Class/Function | Module | Purpose |
|---|---|---|
| `WebBaseLoader` | `langchain_community.document_loaders` | Load web content |
| `PyPDFLoader` | `langchain_community.document_loaders` | Load PDF documents |
| `RecursiveCharacterTextSplitter` | `langchain_text_splitters` | Split documents into chunks |
| `OpenAIEmbeddings` | `langchain_openai` | OpenAI embedding models |
| `InMemoryVectorStore` | `langchain_core.vectorstores` | In-memory vector storage |
| `VectorStoreRetriever` | `langchain_core.vectorstores` | Retriever wrapping vector store |
| `@tool` | `langchain.tools` | Decorator to create retrieval tools |
| `create_agent` | `langchain.agents` | Create RAG agent |
| `@dynamic_prompt` | `langchain.agents.middleware` | Inject retrieval context into prompts |

## Best Practices

- Choose agentic RAG for complex, multi-step queries requiring contextual decision-making
- Choose two-step chains for straightforward questions with guaranteed retrieval needs
- Use `chunk_overlap` to prevent losing context at chunk boundaries
- Set appropriate `k` values in similarity search to balance relevance and context size
- Use `response_format="content_and_artifact"` to keep raw documents accessible alongside serialized text
- Connect existing knowledge bases (SQL, CRMs) as agent tools rather than rebuilding them
- Enable LangSmith tracing for debugging and monitoring retrieval pipelines
- Use MMR search type when you need diverse results, not just the most similar
