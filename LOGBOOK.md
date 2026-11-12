<div align="center">

# 🧠 Building Autonomous AI Agents From Scratch
### *A Developer's Production Engineering Logbook & Architecture Journal*

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Ollama](https://img.shields.io/badge/Ollama-Local_Inference-000000?style=for-the-badge&logo=ollama&logoColor=white)](https://ollama.com/)
[![Model](https://img.shields.io/badge/Model-Qwen_2.5_1.5B-FF6F00?style=for-the-badge&logo=ai&logoColor=white)](https://huggingface.co/Qwen/Qwen2.5-1.5B)
[![Git](https://img.shields.io/badge/Version_Control-Git-F05032?style=for-the-badge&logo=git&logoColor=white)](https://git-scm.com/)

---

*This logbook documents the step-by-step engineering progression from a raw one-shot script into a modular, production-ready, multi-step autonomous AI agent.*

</div>

<br />


---

## 🚀 [Phase 1] - Foundation, Local LLM Setup & Interactive Chat Loop

> **Milestone Focus:** Lectures 1–4  
> **Status:** `COMPLETED`  
> **Hardware Profile:** Intel Core i3 (CPU inference, 0 Cloud API cost)  
> **Active Model:** `qwen2.5:1.5b` (via local Ollama server on `:11434`)

```
┌─────────────────┐       HTTP REST (Port 11434)       ┌────────────────────────┐
│  Python Client  │ ─────────────────────────────────> │     Ollama Engine      │
│  (main script)  │ <───────────────────────────────── │ (qwen2.5:1.5b weights) │
└─────────────────┘             OpenAI Format          └────────────────────────┘
```

---

### 1. Executive Summary

In this milestone, we moved from zero to a fully operational, offline conversational AI assistant. Rather than relying on cloud APIs, we spun up a private local inference server. We established standard software engineering practices early:
- **Sandbox Isolation:** Enforced clean dependency tracking using virtual environments.
- **Config Decoupling:** Isolated sensitive connection URLs and model metadata from source code.
- **Continuous Session Runtime:** Built a resilient command-line interactive loop with graceful termination signals.

---

### 2. Deep-Dive Architectural Concepts (The "Why")

#### 🔒 Virtual Environment Isolation (`.venv`)
Global `pip` installs contaminate your operating system's base Python directory. If Project A depends on `library v1.0` and Project B requires `library v2.0`, updating one breaks the other. 

> [!NOTE]
> `.venv` creates a sandboxed directory containing its own Python executable and site-packages folder. Everything installed remains confined to this repository.

#### ⚡ Hardware-Conscious Model Selection (`qwen2.5:1.5b` vs `qwen3:4b`)
While larger parameter models offer broader world knowledge, they impose heavy computational overhead:

| Metric | `qwen3:4b` (4 Billion Params) | `qwen2.5:1.5b` (1.5 Billion Params) | Winner for Intel i3 |
| :--- | :--- | :--- | :--- |
| **RAM Footprint** | $\approx$ 3.2 GB to 4.0 GB | $\approx$ **986 MB** | **`1.5b`** (Prevents OS swapping) |
| **CPU Token Generation** | Slow / high thermal throttling | **Fast & responsive** | **`1.5b`** (Smooth CLI stream) |
| **Native Function Calling** | Full native support | **Full native support** | **Tie** |

#### 🌐 The OpenAI API Specification as an Industry Standard
Ollama serves models via an OpenAI-compliant REST interface at `http://127.0.0.1:11434/v1`. 

> [!TIP]
> By using `from openai import OpenAI` configured with our local `base_url`, the codebase remains portable. Swapping from local development to production OpenAI (`gpt-4o`) or Anthropic requires updating only configuration variables, not the agent logic.

#### 🧩 Configuration Decoupling (`.env` & `python-dotenv`)
Hardcoding secrets or addresses directly in application files creates technical debt and security risks:
- Built-in `os.getenv()` inspects RAM (`os.environ`).
- `python-dotenv` bridges physical storage and memory: `load_dotenv()` reads key-value pairs from `.env` on disk and populates the active process environment.

---

### 3. Terminal Command Reference

#### 📦 A. Environment & Dependencies

| Command | Action Performed | Engineering Purpose |
| :--- | :--- | :--- |
| `python -m venv .venv` | Generates `.venv/` sandbox | Prevents polluting system-level Python libraries. |
| `.\.venv\Scripts\Activate.ps1` | Activates environment | Points terminal session to isolated `.venv` binaries. |
| `python -m pip install openai python-dotenv` | Installs core client libraries | Direct binary execution avoids broken path launcher errors. |
| `python -m pip freeze > requirements.txt` | Pins package dependencies | Ensures environment reproducibility across machines. |

#### 🦙 B. Model Server Management (Ollama)

```powershell
# Pull and initialize model weights directly into local RAM
ollama run qwen2.5:1.5b

# Inspect all locally cached models and SHA256 identifiers
ollama list
```

#### 🐙 C. Version Control Workflow (Git)

```powershell
# 1. Initialize local repository
git init

# 2. Stage new files (respecting .gitignore)
git add .

# 3. Commit with standard semantic messaging
git commit -m "feat: implement baseline interactive assistant with dotenv and qwen2.5:1.5b"

# 4. Link to remote GitHub server & push
git branch -M main
git remote add origin https://github.com/<your-username>/ai-agent-scratch.git
git push -u origin main
```

---

### 4. Code Implementation & Walkthrough

File: `simple_ai_assistant.py`

```python
import os
from openai import OpenAI
from dotenv import load_dotenv

# -------------------------------------------------------------
# 1. Environment Configuration
# -------------------------------------------------------------
load_dotenv()

# -------------------------------------------------------------
# 2. Client Initialization (Targeting Local Ollama Engine)
# -------------------------------------------------------------
client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)

model_name = os.getenv("MODEL")
print(f"🚀 Assistant online. Engine: [{model_name}]")
print("💬 Type 'exit', 'quit', or 'bye' to terminate.\n" + "-" * 50)

# -------------------------------------------------------------
# 3. Interactive REPL Chat Loop
# -------------------------------------------------------------
while True:
    try:
        user_input = input("\n👤 User: ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\n\nSession terminated by user signal.")
        break

    # Graceful exit interceptor
    if user_input.lower() in ["exit", "quit", "bye", "goodbye"]:
        print("🤖 Assistant: Shutting down. Goodbye!")
        break

    # Avoid unnecessary inference on empty inputs
    if not user_input:
        continue

    # Dispatch payload to LLM
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "user",
                "content": user_input
            }
        ]
    )

    # Extract primary choice payload
    reply = response.choices[0].message.content
    print(f"🤖 Assistant: {reply}")
```

---

### 5. Engineering Analysis: Identified Cons & Trade-Offs

While functional, this baseline exhibits architectural bottlenecks:

```
[User Turn 1] "My name is Alex"     ──> [Sent: Turn 1 Only]     ──> Model acknowledges name
[User Turn 2] "What is my name?"    ──> [Sent: Turn 2 Only]     ──> Model: "I don't know your name"
```

> [!WARNING]
> **Defect 1: Statelessness & Lack of Memory**  
> Large Language Models maintain zero internal state between API calls. In our loop, `messages` is created brand new on each prompt. The model receives no history of previous turns.

> [!WARNING]
> **Defect 2: Rigid Personality & Behavior**  
> We haven't defined a system persona or operational guardrails. The model operates in default conversational mode without domain constraints or output formatting rules.

> [!WARNING]
> **Defect 3: Blocking I/O & High Latency**  
> The terminal blocks until the model finishes generating its entire completion before printing. There is no real-time word-by-word streaming.

---

### 6. The Bridge to Phase 2

To resolve **Defect 1**, the next milestone will introduce **Context & Memory Engineering**:

1. Initialize a long-lived conversation data structure: `messages = []`.
2. Append user input turns (`role: "user"`).
3. Append assistant responses (`role: "assistant"`).
4. Send the accumulated history array on every inference pass to enable multi-turn context retention.

---
## 🧠 [Phase 2] - Day 2: Memory Engineering & Handling LLM Statelessness

> [!IMPORTANT]
> **Milestone Goal:** Eliminate the assistant's short-term amnesia by maintaining an accumulating conversation history array (`messages = []`) across turns.

### 1. 📋 What We Built Today
We upgraded our baseline chatbot from a stateless single-turn responder into a stateful multi-turn conversational assistant. By capturing both `"user"` inputs and `"assistant"` replies inside a persistent list outside the main execution loop, the model can now reference earlier facts, names, and context within the active session.

---

### 2. 💡 Core Concepts: The "Why" Behind Each Decision

- **Statelessness of LLMs**
  - Large Language Models do not store session memory on their servers. The moment an API request completes, the model wipes its working memory clean—every new API call is treated like a brand-new conversation from a stranger.
- **The Context Illusion (How ChatGPT/Claude Remember)**
  - Applications simulate memory by recording the entire back-and-forth conversation locally and sending the **full message array** back to the model on every single turn. Role tags (`"user"` and `"assistant"`) let the LLM distinguish who said what.
- **The Context Window Catch**
  - Every LLM has a strict maximum token limit it can process in a single request (its **Context Window**). Because the entire message list is resent every turn, token usage grows continuously—eventually slowing down inference on CPU hardware, increasing API costs, or truncating older messages.

```text
Turn 1: [ User("Hi, I'm Abhishek") ] ──► LLM ──► Assistant("Hello Abhishek!")
Turn 2: [ User("Hi..."), Assistant("Hello..."), User("What's my name?") ] ──► LLM ──► Assistant("Your name is Abhishek.")


---

---

## 🎭 [Phase 3] - Day 3: System Prompts, Personas & RCTEF Framework

> [!IMPORTANT]
>
> **Milestone Goal:** Control the assistant's personality, tone, and output structure by pinning a `"system"` role instruction at the top of the message history.

### 1. 📋 What We Built Today
We gave our stateful assistant a defined persona and strict behavioral boundaries. By initializing `messages` with a `"system"` dictionary before the chat loop starts, every API call now instructs `qwen2.5:1.5b` on *how* to respond before it reads what the user asked.

---

### 2. 💡 Core Concepts: The "Why" Behind Each Decision

* **The `"system"` Role (Developer Instructions)**
  * Unlike `"user"` (human queries) and `"assistant"` (AI replies), `"system"` (called `"developer"` in newer OpenAI specs) sets global behavioral rules hidden from the end user.
* **Why It Goes Outside the Loop (Index `0`)**
  * Placing the system message once at index `0` ensures it stays permanently pinned at the top of every request without duplicating tokens on every loop iteration.
* **RCTEF Prompt Engineering Framework**
  * **R**ole (Persona) $\rightarrow$ **C**ontext (Scenario) $\rightarrow$ **T**ask (Goal) $\rightarrow$ **E**xamples (Few-shot) $\rightarrow$ **F**ormat & Constraints (Length/style limits).

---

### 3. 💻 Code Implementation (`simple_ai_assistant.py`)

```python
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)

model_name = os.getenv("MODEL")

SYSTEM_PROMPT = (
    "Role: You are a concise, humble, and practical AI Engineering Mentor. "
    "Context: You are helping a developer build AI agents from scratch in Python. "
    "Task: Answer questions clearly with practical reasoning. "
    "Constraints: Keep every response under 60 words. Use bullet points when listing steps."
)

# Pinned once at index 0 before the loop starts
messages = [
    {
        "role": "system",
        "content": SYSTEM_PROMPT
    }
]

while True:
    try:
        user_input = input("\nUser: ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\nSession ended.")
        break

    if user_input.lower() in ["exit", "quit", "bye", "goodbye"]:
        print("Assistant: Goodbye!")
        break

    if not user_input:
        continue

    messages.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model=model_name,
        messages=messages
    )

    reply = response.choices[0].message.content
    print("Assistant: " + reply)

    messages.append({"role": "assistant", "content": reply})