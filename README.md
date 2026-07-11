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
- **Vector Similarity Search:** in-memory cosine similarity (`scikit-learn`) over saved embeddings — *(ChromaDB is installed and was used/tested during development; the live app currently does not use it — see Known Limitations)*
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

## Known Limitations 

- **Embeddings:** Milestone 1 originally done with TF-IDF vectorization as a substitute for sentence-transformers, due to an unresolved PyTorch DLL error on Windows. The root cause was later identified as Windows' default file path length limit, fixed by enabling Long Path support, and the project now uses real `sentence-transformers` (`all-MiniLM-L6-v2`) embeddings.

- **Vector search:** ChromaDB was used and verified correct (including fixing a distance-metric bug — it defaults to Euclidean/L2 distance, not cosine, unless explicitly configured). Persistent, disk-backed ChromaDB storage proved unreliable on this Windows machine (file-locking, corrupted index issues), so the current live app uses an in-memory cosine-similarity search instead, which is mathematically equivalent for this dataset size.

- **Agents:** The 5-agent pipeline (Triage, Log Analysis, Root Cause, Duplicate Detection, Remediation) shown in the architecture diagram is currently design-only — not yet implemented in code. This was outside Milestone 1's required scope (Bug Submission Module + working RAG pipeline).

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
- [ ] Agents 1-5: Coded implementation (currently design-only, see `docs/03_agents.md`)
