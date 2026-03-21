# Deep Dive Phase 3: The OASIS Simulation Sandbox

Phase 3 is the "Engine Room." This is where the **Agents** live, breathe, and fight. The simulation is a **Non-Deterministic, Stochastic Environment**.

---

## 1. The Simulation Orchestrator (`run_parallel_simulation.py`)
MiroFish runs two platform engines (Twitter/Reddit) in a synchronized parallel loop.

### A. The "Clock" Thread
*   **Logical Unit:** **Round** (representing 30–60 minutes).
*   **Loop Depth:** If `total_hours = 72` and `minutes_per_round = 60`, MiroFish executes **72 iterations**.
*   **The Problem:** Running 1,000 LLM calls simultaneously crashes modern APIs.
*   **The Math (Semaphore):** 
    *   `Semaphore = 30` (Maximum concurrent LLM requests).
    *   This ensures high-speed execution without being rate-limited.

---

## 2. Stochastic Agent Activation (The "Wake Up" Logic)
Inside `get_active_agents_for_round`, we decide who joins the simulation each hour. 

### The Activation Probability ($P$):
For every agent $i$:
$$P_i = \begin{cases} \text{activity\_level}_i \times \text{multiplier}_t & \text{if } t \in \text{active\_hours}_i \\ 0 & \text{otherwise} \end{cases}$$
*   **Target Count Gate:** From the population of $P_i > \text{rand}(0,1)$, we use `random.sample` to pick $N$ agents. 
*   **The Logic:** Even if an agent is "awake," they might not post. This mimics **human choice**. A "Lurker" agent ($0.1$ activity) rarely wakes up, while an "Influencer" ($0.9$ activity) is almost always active.

---

## 3. The Digital "Sense-Think-Act" Loop
This is the core cognitive architecture of the agent.

### Step 1: Sensing (Contextual Feed)
The agent sees a "Screen." It is **not** a full list of all posts.
*   **The Feed Filter:** OASIS implements a simple Recommendation Engine.
    *   **Recency (t):** $Score \propto 1/t$
    *   **Engagement (L):** $Score \propto \log(L+1)$
    *   **User Affinity (A):** Based on the "Follow" graph node distance.

### Step 2: Thinking (LLM Reasoning)
Thinking uses the **OASIS Agent Prompt**.
*   **Inputs:** Persona + Feed + History.
*   **Reasoning:** The LLM does a "Persona-Alignment Check."
    *   *Prompt:* "You see [Post X]. Based on your [Bio], would you react?"
*   *Math:* This is the most computationally expensive part. We use high-reasoning models (GPT-4o/Claude 3.5) here to ensure "In-character" dialogue.

### Step 3: Acting (The Decision)
The LLM outputs a **Structured Action**.
*   **Action Types:** 
    *   `CREATE_POST`: High cost, high reach.
    *   `LIKE`: Low cost, low reach (affects ranking).
    *   `REPLY`: Medium cost (triggers notifications).
    *   `DO_NOTHING`: High frequency for low-activity agents.

---

## 4. The World Database (Persistence)
The simulation doesn't "feel" like it’s thinking until it has **External Persistence**.
*   **Shared Infrastructure:** `twitter_simulation.db` and `reddit_simulation.db` (SQLite).
*   **Interaction Physics:** When Agent A replies to Agent B, it updates a `parent_id` link in the SQL table. This creates the **Thread Tree**. 
*   **The Result:** Agents in Round 4 can read the threaded discussions from Round 3. This is how **Social Context** is built.

---

## 5. Parallel Platform Sync
`run_parallel_simulation.py` ensures that if an event happens on Twitter, it eventually "drifts" to Reddit. 
*   The **Zep Memory Manager** acts as the cross-bridge. 
*   Twitter agents "write" their findings to the graph. 
*   Reddit agents "read" those findings during their next search action. 
*   **The Emergence:** Misinformation on Twitter might trigger a "Fact-Check" thread on Reddit. 

[Go to Phase 4: Agentic Analysis and ReACT Report](./Phase_4_Agentic_Analysis_and_ReACT_Report.md)
