# Deep Dive Phase 1: Knowledge Graph & Ontology (GraphRAG)

Phase 1 is where MiroFish converts your static "Source of Truth" (PDFs, Word docs, etc.) into a structured, queryable digital world. This is not a simple vector search; it is a **Semantic Extraction** process.

---

## 1. The 50,000 Character Barrier: The Math of Context
MiroFish currently caps the input text at **50,000 characters** for the Ontology stage.
*   **The Problem:** LLMs have "Attention Fatigue." If you feed 1,000 pages of text to extract entities, the model often misses subtle relationship chains or starts hallucinating.
*   **The Math:** 
    *   `1 Token ≈ 4 Characters`.
    *   `50,000 Characters ≈ 12,500 Tokens`.
    *   Most modern models (GPT-4o, Claude 3.5) have a context window of 128k+, but the **Instruction Following** accuracy drops significantly after 15k tokens specifically for "dense extraction" tasks.
*   **The Strategy:** We use the most context-rich 50k characters (usually the beginning and significant summaries) to define the **Ontology Schema**, and then use the full document for the subsequent Graph density updates.

---

## 2. Ontology Generation: The "Social DNA"
The `OntologyGenerator.py` executes the most important prompt in the pipeline. It doesn't just look for keywords; it looks for **Social Interaction Patterns**.

### The Extraction Logic (ReACT Pattern)
The LLM is given a role: **"You are a World-Building Architect."** 
It follows these steps:
1.  **Iterative Extraction:** It reads the text in chunks and identifies **Entities** (People, Organizations, Groups).
2.  **Schema Classification:** It maps every entity to an OASIS-compatible type (e.g., `PublicFigure`, `Student`, `MediaOutlet`).
3.  **Relationship Weighting:** Instead of just saying "A knows B," it assigns a **Relationship Weight (0-1)** based on context.
    *   *Mathematical Impact:* High-weight relationships (0.8+) trigger stronger "Friendship" algorithms in the simulation sandbox later on.

---

## 3. The Zep Knowledge Graph (The Memory Bank)
Once the entities are extracted, they are uploaded to **Zep Cloud**.

### Code Deep-Dive: `ZepGraphMemoryUpdater`
```python
# How we map your data to Zep Graph
async def add_documents_to_graph(self, documents: List[Dict[str, Any]]):
    # 1. We vectorize the document (Semantic Search foundation)
    # 2. We perform "Sub-Graph Isolation":
    #    Every fact is linked to an entity. 
    #    "Fact: Dean Smith resigned" --(LINKED_TO)--> "Entity: Dean Smith"
```

### Why this matters for the simulation:
When an agent "thinks" during the simulation, it doesn't search the whole internet. It performs a **Graph-Grounded Retrieval (GraphRAG)**. 
*   **Logic:** If Agent A sees a post about "Tuition," the system performs a `near_entity` search on Agent A’s graph node.
*   **Math:** It only retrieves facts within **2 degrees of separation** from that agent. This simulates "limited perspective"—an agent only knows what its character *would* know.

---

## 4. Grounding and Evolution
The graph is not static.
*   **Round 0:** The graph contains facts from your PDF.
*   **Round 10:** The graph now contains **New Nodes** representing the actions agents took in the simulation.
*   **The Result:** The simulation "learns" from itself. If a protest starts in the sandbox, that protest becomes a fact in the graph, which then influences the "thinking" of agents in Round 11.

[Go to Phase 2: Persona Creation and Simulation Config](./Phase_2_Persona_Creation_and_Simulation_Config.md)
