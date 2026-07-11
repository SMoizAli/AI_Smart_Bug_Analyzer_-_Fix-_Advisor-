# AI Smart Bug Analyzer & Fix Advisor (Group 1)

An AI-powered system that takes in bug reports, stack traces, or error logs, and uses a **multi-agent pipeline** combined with a **RAG (Retrieval-Augmented Generation)** knowledge base of historical defects to triage, analyze, and suggest fixes for software bugs.

This is a solo InfosysSpringboard internship project, built entirely in Python by me.

---

## How it works (high level)

> User
>
>   ↓
>
>
> Bug Submission Module  (accepts text paste or file upload)
>
>   ↓
>
>
> [Bug report gets stored + embedded]
>
>   ↓
>
> Multi-Agent Pipeline ──────────────┐
>                                                                              
>   ├─ Triage Agent─────────────────                  │
>                                       
>   ├─ Log Analysis Agent─────────────        │  ←── queries ──→  Historical Defect Knowledge Base (Vector DB / RAG)
>                                       
>   ├─ Root Cause Agent──────────────                                │                                    
>                                       
>   ├─ Duplicate Detection Agent─────                    ←──┘                    
>
>   └─ Remediation Agent
>
>   ↓
>
>
> Structured Findings & Resolution Display
>
> 
>


---

The Multi-Agent Pipeline queries a **Historical Defect Knowledge Base** (built using public bug datasets from Mozilla, Apache, and Eclipse via Kaggle) to find similar past bugs and inform its analysis and fix suggestions.

---

## Tech Stack

- **Language:** Python
- **UI / Bug Submission:** Streamlit
- **Embedding Model:** sentence-transformers (`all-MiniLM-L6-v2`)
- **Vector Database:** ChromaDB
- **Chunking:** LangChain text splitters
- **Data Processing:** pandas
- **Agent Orchestration:** Python (custom classes for Milestone 1; may adopt LangChain/CrewAI later)
- **LLM (future remediation generation):** TBD based on access

---

## Project Documentation

Design and research documentation for Milestone 1 (30 June – 9 July):

| Doc | Description |
|---|---|
| [`docs/01_concepts.md`](docs/01_concepts.md) | Study of defect analysis workflows, bug report structure, stack traces, RAG, and semantic similarity |
| [`docs/02_architecture.md`](docs/02_architecture.md) | Overall system architecture, data flow, and tech stack |
| [`docs/03_agents.md`](docs/03_agents.md) | Detailed responsibilities (input/process/output) of all 5 agents |
| [`docs/04_knowledge_base.md`](docs/04_knowledge_base.md) | Historical Defect Knowledge Base record structure and storage design |

---

## Project Structure

docs/         → design documentation and study notes
src/          → application source code (modules, agents)
data/         → datasets (raw and cleaned)
notebooks/    → exploration/testing notebooks (chunking, embeddings, retrieval testing)

---

## Status

- [x] Task 1: Study required concepts
- [x] Task 2: Design system architecture
- [x] Task 3: Define agent responsibilities
- [x] Task 4: Design the knowledge base
- [x] Task 5: Build the Bug Submission Module
- [x] Task 6: Build the Historical Defect Knowledge Base
- [x] Task 7: Data Cleaning
- [x] Task 8: Chunking
- [x] Task 9: Embedding Generation
- [x] Task 10: Vector Database
- [x] Task 11: Retrieval Testing