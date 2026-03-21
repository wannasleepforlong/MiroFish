# MiroFish Architecture Overview

MiroFish is a **Multi-Agent Simulation & Predictive Analysis Platform**. It integrates GraphRAG, Digital Twin Personas, and Orchestrated LLM execution to simulate complex social dynamics.

---

## 1. High-Level Data Flow (ASCII Diagram)

```ascii
[ USER INPUT ] ---> [ PHASE 1: GRAPHRAG ] ---> [ PHASE 2: RESIDENTS ]
      (PDF/Doc)          | Ontology Extraction       | Persona Generation
                         | Zep Graph Memory          | Simulation Config
                         v                           v
[ REPORT / CHAT ] <--- [ PHASE 4: ANALYST ] <--- [ PHASE 3: SANDBOX ]
      (Insight)          | ReACT Investigation       | OASIS Engine (Twitter)
                         | Multi-Agent Interview     | OASIS Engine (Reddit)
                         | Evidence Synthesis        | SQLite Action Persistence
```

---

## 2. Component Architecture

### A. API Layer (The Gateway)
The backend is powered by **Flask** with a Blueprint-based architecture:
*   `graph_bp`: Handles document upload, text extraction, and Zep Graph construction.
*   `simulation_bp`: Manages simulation preparation, preparation tasks, and live interviews.
*   `report_bp`: Triggers report generation and hosts the interactive RAG chat.

### B. Intelligence Layer (The CAMEL-AI Orchestrators)
These services use **CAMEL-AI** to manage autonomous "agent-to-agent" reasoning:
*   **`OntologyGenerator`**: A high-level architect agent that extracts the social schema.
*   **`OasisProfileGenerator`**: A psychologist agent that projects human personas.
*   **`SimulationConfigGenerator`**: A world-builder agent for platform rules.
*   **`ReportAgent`**: A research lead agent that orchestrates specialized tools.

### C. Execution Layer (The Sandbox)
This is where the actual simulation runs:
*   **`SimulationRunner`**: Manages the `subprocess` calls to the OASIS Python scripts.
*   **`run_parallel_simulation.py`**: A synchronized loop that keeps Twitter and Reddit in step.
*   **`ZepGraphMemoryUpdater`**: Bridges the gap between "Simulated Action" and "Long-Term Memory."

### D. Persistence Layer (The Records)
1.  **Zep Cloud**: Stores the Knowledge Graph, entity nodes, and relationship edges. Used for GraphRAG.
2.  **SQLite (`simulation.db`)**: Stores the high-frequency events (Posts, Likes, Comments) for analysis.
3.  **Local Filesystem**: Stores the generated reports, persona profiles, and log files.

---

## 3. Technical Stack Summary

| Layer | Technology |
| :--- | :--- |
| **Frontend** | Vue.js 3, Vite, TailwindCSS |
| **Backend API** | Python, Flask, Gunicorn |
| **Agent Framework** | **CAMEL-AI** (Base Framework) |
| **Simulation Core** | **OASIS** (CAMEL Extension) |
| **LLM Interface** | OpenAI SDK (Standard Protocol) |
| **Graph Memory** | Zep Cloud (GraphRAG) |
| **Local Persistence**| SQLite (Action Traces) |

---

## 5. Agent Orchestration Deep-Dive

MiroFish doesn't just call a single LLM; it uses a **Multi-Agent Orchestrator** pattern.

### The CAMEL-AI / OASIS Core
The simulation engine (`Phase 3`) uses **CAMEL-AI** to create "Role-Playing" agents. Each agent has its own `ChatAgent` instance inside the OASIS environment. 
*   **Decoupled Logic**: The simulator handles the "World Physics" (Likes, Reposts), while CAMEL handles the "Cognitive Reasoning" (Thinking and Generating Content).
*   **Persona Isolation**: Every agent is isolated. They can ONLY access information provided to them via the "Sensing" phase (their digital feed).

### The "Lead Analyst" Orchestration (Phase 4)
The `ReportAgent` acts as a **Lead Investigator** that manages its own "sub-agents" or tools:
1.  **The Planner**: Decodes the user query and sets the investigation roadmap.
2.  **The Researchers (Tools)**: `Insight Forge` and `Panorama Search` act as data-retrieval agents.
3.  **The Correspondent (Interview API)**: Acts as a middleman between the Analyzer and the Sandbox, conducting real-time interviews with the Digital Twins.

This modularity is what allows MiroFish to handle thousands of interactions without losing the context of the original document.

---

## 4. Phase-by-Phase Logic Summary

### Phase 1: Foundation (Text to Knowledge)
*   **Strategy**: Semantic extraction using LLM.
*   **Success Metric**: High relationship density and accurate entity classification.

### Phase 2: Preparation (Knowledge to People)
*   **Strategy**: Generative Persona interpolation.
*   **Success Metric**: Diversity of personality (MBTI, stance) among agents.

### Phase 3: Simulation (People to Interaction)
*   **Strategy**: Stochastic activation and LLM-driven social reasoning.
*   **Success Metric**: Emergent behaviors (viral events, polarization) that weren't in the original text.

### Phase 4: Analysis (Interaction to Meaning)
*   **Strategy**: ReACT-based investigative reporting.
*   **Success Metric**: A report that identifies "Counter-Intuitive Insights" grounded in simulation data.

---

[Back to Documentation Index](../../README.md)
