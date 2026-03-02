# Mutual Fund RAG Chatbot Architecture

This document outlines the architecture and phased implementation plan for the Mutual Fund RAG Chatbot. The chatbot uses Gemini LLM and a Retrieval-Augmented Generation (RAG) pipeline to provide factual information about specific Mutual Fund schemes from Groww.

## Architecture Overview

The system follows a standard RAG pattern with a **Backend (BE) API Layer** (FastAPI) acting as the middleware between the **Frontend (UI)** and the **RAG Pipeline**.

```mermaid
graph TD
    User((User)) --> UI[Streamlit UI]
    UI --> API[Backend API Layer (FastAPI)]
    API --> Controller[Chat Controller]
    Controller --> ScopedChecker{In-Scope / Scheme Check?}
    ScopedChecker -- No --> OutOfScope[Static Disclaimer Response]
    ScopedChecker -- Yes --> RAG[RAG Pipeline]
    
    subgraph phase_1 & phase_2: Data Layer
        Links[Groww Links] --> Scraper[Data Scraper]
        Scraper --> Parser[Structured Parser]
        Parser --> VectorDB[(Vector Database)]
    end
    
    subgraph phase_3 & phase_4: LLM Layer
        RAG --> Embedder[Gemini Embeddings]
        Embedder --> Retrieving[Retriever]
        Retrieving --> Prompt[System Prompt + Guardrails]
        Prompt --> Gemini[Gemini LLM]
        Gemini --> Response[Factual Response + Citations]
    end
    
    Response --> API
    API --> UI
```

---

## Folder Structure

The project is divided into phase-specific folders to ensure modular development and testing.

```text
mutualfund_rag/
├── phase_1/                # Data Acquisition
│   ├── scraper.py
│   ├── tests/              # Automated tests for Phase 1
│   └── data/               # Scraped data (raw)
├── phase_2/                # Vector Database
│   ├── ingest.py
│   ├── tests/              # Automated tests for Phase 2
│   └── chroma_db/          # Persistent Vector DB
├── phase_3/                # RAG & API Layer
│   ├── api.py              # Backend API
│   ├── pipeline.py         # RAG Logic
│   └── tests/              # Automated tests for Phase 3
├── phase_4/                # Guardrails
│   ├── guardrails.py
│   └── tests/              # Automated tests for Phase 4
├── phase_5/                # UI Development
│   ├── app.py              # Streamlit UI
│   └── tests/              # UI Integration tests
└── phase_6/                # Evaluation & Final Testing
```

---

## Phased Implementation & Testing

### Phase 1: Data Acquisition & Preprocessing
**Goal**: Convert raw web data from provided links into a structured knowledge base.
- **Tools**: `httpx`, `BeautifulSoup`.
- **Automated Tests**:
    - `test_scraping_completion`: Verify all 7 target URLs are successfully scraped.
    - `test_data_integrity`: Ensure generated JSON/Markdown files contain essential fields (NAV, Fund Size, etc.).

### Phase 2: Embedding & Vector Database Setup
**Goal**: Create a searchable index of the mutual fund data.
- **Tools**: `ChromaDB`, Gemini Embedding Model (`text-embedding-004`).
- **Automated Tests**:
    - `test_vector_db_persistence`: Verify ChromaDB files are created and non-empty.
    - `test_embedding_retrieval`: Verify that a simple query returns at least one document from the vector store.

### Phase 3: BE API & RAG Pipeline Development
**Goal**: Create the Backend API and RAG pipeline.
- **Tools**: `FastAPI`, `LangChain`, `Gemini Pro`.
- **Automated Tests**:
    - `test_api_connection`: Verify the FastAPI server is reachable.
    - `test_retriever_logic`: Verify that the retriever fetches relevant documents for specific fund names.
    - `test_citation_mapping`: Verify that the response includes correct source URLs.

### Phase 4: Guardrails & Prompt Engineering
**Goal**: Ensure compliance, factual accuracy, and scope adherence.
- **Automated Tests**:
    - `test_advice_filter`: Query "Should I invest?" -> Expect disclaimer.
    - `test_out_of_scope_filter`: Query "Weather in Delhi" -> Expect out-of-scope response.
    - `test_unknown_scheme_filter`: Query "HDFC Fund" -> Expect "I dont have information regarding the scheme".

### Phase 5: UI Development (Streamlit)
**Goal**: Provide a user-friendly chat interface connected to the BE API.
- **Tools**: `Streamlit`.
- **Automated Tests**:
    - `test_ui_api_integration`: Verify that the UI successfully sends a message to the API and displays the response.

### Phase 6: Final Verification
**Goal**: End-to-end validation.
- **Automated Tests**:
    - Full E2E suite covering all functional requirements and financial guardrails.

---

## Knowledge Base (Scope)
The chatbot is strictly limited to the following 7 schemes:
1. [Axis Liquid Direct Fund](https://groww.in/mutual-funds/axis-liquid-direct-fund-growth)
2. [Axis ELSS Tax Saver](https://groww.in/mutual-funds/axis-elss-tax-saver-direct-plan-growth)
3. [Axis Flexi Cap Fund](https://groww.in/mutual-funds/axis-flexi-cap-fund-direct-growth)
4. [Axis Large Cap Fund](https://groww.in/mutual-funds/axis-large-cap-fund-direct-growth)
5. [Axis Midcap Fund](https://groww.in/mutual-funds/axis-midcap-fund-direct-growth)
6. [Axis Small Cap Fund](https://groww.in/mutual-funds/axis-small-cap-fund-direct-growth)
7. [Axis Focused Direct Plan](https://groww.in/mutual-funds/axis-focused-direct-plan-growth)
