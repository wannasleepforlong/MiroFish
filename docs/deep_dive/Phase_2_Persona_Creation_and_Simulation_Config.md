# Deep Dive Phase 2: Persona Creation & Simulation Config

Phase 2 is the most creative stage. MiroFish takes the **Static Nodes** from Phase 1 and "dreams up" a full human life for every single one of them.

---

## 1. Persona Generative Architecture (`OasisProfileGenerator.py`)
MiroFish creates agents that aren't just names; they are **Semantic Personalities**.

### The Math of Personas (LLM Synthesis)
The `OasisProfileGenerator` takes your graph context and asks the LLM to "Interpolate" (not extrapolate) human details.
1.  **Identity Sampling (1-to-1):** Every `Entity` node becomes 1 `Agent Profile`.
2.  **Context Loading:** 
    *   `Top K Facts (K=10)` about that entity are pulled from the Zep graph.
    *   `K` is chosen to fit within a 2k-character bio without redundant noise.
3.  **Personality Projection:** 
    *   The LLM assigns an **MBTI type** (1 of 16).
    *   It assigns **Social Media Usage Metrics** (Posting freq 0-1, Sentiment bias -1 to +1).
*   **Result (Bio):** 
    *   *Input:* "John is a student. He hates tuition hikes."
    *   *Output:* "John (20, Senior). Introvert (INTP). Loves digital privacy (0.9 weight). Posts twice daily. Uses sarcastic, millennial-style slang."

---

## 2. Platform-Specific Physics (Twitter vs Reddit)
The system generates two different formats because OASIS treats Twitter and Reddit very differently.

### Twitter Simulation Configuration:
*   **Format:** `.csv`.
*   **Physics:** Twitter agents prioritize **Short, Viral Bursts**.
*   **Math:** The environment uses a **Follower Graph**. An agent's "Reach" is determined by how many other agents the system "autolinks" to them during setup.

### Reddit Simulation Configuration:
*   **Format:** `.json`.
*   **Physics:** Reddit agents prioritize **Threaded Deep-Dives**.
*   **Math:** The environment uses **Subreddits** (Topic Clusters). An agent’s probability of seeing a post is based on "Topic Overlap" (`Agent Topic Vector` ⋅ `Post Topic Vector`).

---

## 3. Environment Engineering (`SimulationConfigGenerator.py`)
This is the "Rules of the World" for the sandbox. It sets the **Global Simulation Parameters**.

### A. The Hourly Multiplier (The "Human Sleep" Cycle)
The system calculates a base activity target for every platform.
*   **The Math:** 
    *   `Base Count = (Base Min, Base Max)`
    *   `Peak Activity Multiplier = 1.5` (e.g., 6 PM - 10 PM)
    *   `Off-Peak Multiplier = 0.3` (e.g., 1 AM - 5 AM)
*   **Regional Logic:** If the user specifies "India-based simulation," the peak hours shift to IST. This ensures your simulation feels realistic for that specific time zone.

### B. Event Configuration: "The Spark"
The LLM generates **Seed Posts** (Initial Posts) to start the simulation.
*   **Poster Type Matching:** The system doesn't just make a random agent post. It asks: "Which agent profile has the highest semantic similarity to this Topic?"
*   *Math:* It picks the agent with the highest **Cosine Similarity** to the seed event's content. This ensures the "University Account" posts the "University Announcement," not a random student.

---

## 4. Automation and Retries: Handling LLM Failure
In `Phase 2`, the LLM output is a large JSON. 
*   **The Conflict:** Long JSON often hits model output limits or gets truncated.
*   **The Logic:** `SimulationConfigGenerator` uses **Recursive Correction**. If the JSON is invalid, it doesn't fail; it feeds the error back to the LLM and asks for a "Schema-valid segment" to patch the missing data.

[Go to Phase 3: The OASIS Simulation Sandbox](./Phase_3_The_OASIS_Simulation_Sandbox.md)
