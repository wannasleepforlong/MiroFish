# Deep Dive Phase 4: Agentic Analysis & ReACT Report

Phase 4 is the final stage. MiroFish acts as an **Independent Auditor** that reviews the simulation and tells you, the user, what happened and what it means.

---

## 1. The ReACT Investigator (`ReportAgent.py`)
MiroFish uses the **ReACT (Reasoning + Acting)** loop to write its report. This is not a static summarization; it’s an active **Investigation**.

### The Multi-Step Thinking Loop
Inside the `ReportAgent.generate_report` function (line 151), the LLM undergoes a four-step loop for **every section**:
1.  **Thought:** "I need to understand if the media influenced the students' stance."
2.  **Action:** The Agent calls one of its specialized **Zep Tools**.
3.  **Observation:** The Agent reads the tool output (e.g., student interview results).
4.  **Repeat:** It performs this loop 2–5 times to build an "Evidence Base" before writing the final markdown.

---

## 2. The Zep Analysts (The Tool Chest)
MiroFish gives the `ReportAgent` four "superpowers" through its `ZepToolsService`:

### A. Insight Forge (The Deep Search)
*   **Logic:** It breaks a complex question into **Sub-Questions**.
    *   *Question:* "How did the university react?"
    *   *Sub-Questions:* "What did the Dean post?", "What was the official statement?", "How many students liked it?"
*   **The Math:** It performs a **Hybrid Search** (Vector Search + Keyword Search) in the Zep graph to find the most relevant "Fact Nodes."

### B. Panorama Search (The Global View)
*   **Logic:** It differentiates between **Current Facts** and **Historical Evolution**.
*   **Insight:** It traces how a "Rumor" (Phase 1 fact) became "Verified" (Phase 3 simulation action). This shows you the **Information Cascade**.

### C. Interview API (The Reporter)
*   **Logic:** This is the most complex "Tool Call." It actually **reinvigorates an agent's persona** from the sandbox and asks it a question.
*   **The Bridge:** It sends a POST request to the simulation runner's `/interview` endpoint.
*   **Return:** You get a **Direct Quote** (e.g., "@dean_smith: 'I was just following the budget guidelines'"). This adds "human flavor" to the report.

---

## 3. The Report Synthesizer (Markdown Generation)
After all investigations are complete, the `ReportAgent` synthesizes its findings into a structured document.

### The Sectioning Constraints
The synthesizer must follow strict formatting rules (`SECTION_SYSTEM_PROMPT_TEMPLATE`):
*   **No Headers:** The system manages headers automatically to keep the report clean.
*   **Balanced Sourcing:** It must balance content between:
    *   **Document Context (Grounding)**
    *   **Live News (External Factors)**
    *   **Simulation Log (Simulated Behavior)**
*   **The Analysis Layer:** It specifically looks for "Predictive Insights" (e.g., "Given the current momentum, if the budget isn't adjusted within 6 months, the simulation predicts an 80% chance of a full-scale strike.")

---

## 4. The Interview Layer (Post-Report Chat)
The report is not the end. The `ReportAgent` becomes a **Chatbot** for your simulation.

### The "Report Chat" Logic:
1.  **Context Loading:** It loads the entire generated report into its context window.
2.  **RAG-Enhanced Answering:** When you ask, "Why did the media side with the students?", it doesn't just guess; it uses its tools to dig back into the **GraphRAG** and find the specific media accounts that posted in Round 3.

### Summary of the Lifecycle
*   **Phase 1:** Your Data (Knowledge)
*   **Phase 2:** The People (Personas)
*   **Phase 3:** The Event (Simulation)
*   **Phase 4:** The Meaning (Report)

[Back to Introduction](../../README.md)
