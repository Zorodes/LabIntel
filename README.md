# LabIntel

### AI Engineering Copilot powered by RAG, MCP, and LLM Agents

LabIntel is an AI-powered engineering assistant that combines Retrieval-Augmented Generation (RAG), the Model Context Protocol (MCP), and LLM agents to answer engineering questions and perform domain-specific calculations using custom tools.

The project is designed for engineering domains such as chemical, mechanical, aerospace, manufacturing, and energy.

---

## Features

- Retrieval-Augmented Generation (RAG) for engineering documents
- Semantic search using vector embeddings
- ReAct agent for reasoning and tool selection
- Custom engineering tools exposed through MCP
- Automatic tool discovery using FastMCP
- Reactor engineering calculations
- Process safety limit checking
- Context-aware responses powered by Groq

---

## Architecture

```text
                    User Query
                        │
                        ▼
            LlamaIndex ReAct Agent
               │               │
               │               ▼
               │          Groq LLM
               │
               ▼
         BasicMCPClient
               │
               ▼
          FastMCP Server
               │
               ▼
      Engineering Tool Library

               ▲
               │
        ChromaDB Vector Store
               ▲
               │
     Engineering Documents (PDFs)
```

---

## Tech Stack

| Component | Technology |
|------------|------------|
| Language | Python |
| Agent Framework | LlamaIndex |
| LLM | Groq API |
| Tool Protocol | MCP (FastMCP) |
| Vector Database | ChromaDB |
| Embedding Model | Nomic Embed |
| Retrieval | RAG |

---

## Project Structure

```text
LabIntel/
│
├── agent.py
├── mcp_server.py
├── rag_v1.py
├── tools/
│   ├── __init__.py
│   └── req_tools.py
├── documents/
├── README.md
└── requirements.txt
```

---

## Engineering Tools

- Calculate CSTR Volume
- Calculate Residence Time
- Calculate PFR Conversion
- Check Process Safety Limits

---

## Why LabIntel?

Traditional document-based chatbots can retrieve relevant information but cannot perform engineering-specific computations.

LabIntel combines RAG with the Model Context Protocol (MCP), allowing an AI agent to retrieve engineering knowledge and invoke specialized calculation tools whenever numerical analysis is required. This enables more accurate, explainable, and context-aware engineering assistance.

---

## Development Progress

- [x] Phase 1 — RAG Pipeline
- [x] Phase 2 — MCP Server and ReAct Agent Integration
- [ ] Phase 3 — Backend API
- [ ] Phase 4 — User Interface
- [ ] Phase 5 — Persistent Chat History
- [ ] Phase 6 — Multi-Document Retrieval
- [ ] Phase 7 — Production Deployment

---

## Future Work

- Develop a web-based user interface
- Connect it with backend
- Add persistent chat history using SQLite or PostgreSQL
- Support multiple uploaded engineering documents
- Add authentication and user management
- Containerize the application using Docker
- Deploy the application to the cloud
