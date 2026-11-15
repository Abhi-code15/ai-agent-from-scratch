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
```

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
```

---

## 🛠️ [Phase 4] - Tool Calling: Teaching Our AI to Use Real-World Tools (Videos 7 & 8)

> **Milestone Focus:** Videos 7 & 8 (CodeWithMik AI Engineering Series)  
> **Topic:** Tool Calling Basics & Functions with Parameters  
> **Status:** `COMPLETED`  
> **Hardware Profile:** Intel Core i3 (CPU inference, 100% Free / Local)  
> **Active Model:** `qwen2.5:1.5b` (via local Ollama server on `:11434`)  
> **New Role Learned:** `"tool"` (We now know all 4 roles: `"system"`, `"user"`, `"assistant"`, `"tool"`)

---

### 1. 🎯 The Big Problem & The Solution

Before this lecture, our AI was living inside a closed box. It only knew what it learned during training.

| User Question | ❌ Without Tools | ✅ With Tools (Phase 4) |
| :--- | :--- | :--- |
| **"What time is it now?"** | *"I cannot check the live time. I am just an AI."* | Calls `get_current_time()` $\rightarrow$ *"It is 8:30 PM."* |
| **"What is the weather in Delhi?"** | *"I don't have live internet data."* | Calls `get_city_weather("Delhi")` $\rightarrow$ *"Delhi is 23°C."* |
| **"Hi, how are you?"** | *"I am doing well! How can I help?"* | Speaks directly (no tools needed). |

> [!NOTE]
> **The Golden Rule of Tool Calling:**  
> **The AI NEVER runs the code.** The AI only *decides* which tool to call and extracts the arguments. **Your Python program runs the actual code.**

---

### 2. 💡 Easy Analogy: The Restaurant Menu

Think of tool calling like ordering food at a restaurant:

```text
1. The Menu (tools.py)        ──► You give the AI a menu of tools: "get_current_time", "get_city_weather".
2. The Order (LLM Decision)   ──► The AI cannot cook. It writes an order ticket: {"tool": "get_city_weather", "city": "Delhi"}.
3. The Kitchen (Python Code)  ──► Your Python program cooks the food (calls wttr.in weather API).
4. The Food (Tool Result)     ──► Python puts the result on a plate with the ticket ID (role="tool", tool_call_id=...).
5. The Serving (Final Answer) ──► The AI takes the food, adds polite words, and serves it to the user.
```

---

### 3. 🔄 How It Works Step-by-Step (The 2-API Call Dance)

Notice that for every question needing a tool, we make **TWO calls** to Ollama:

```text
User asks: "What is the weather in Delhi?"
   │
   ▼
[API Call #1] Send (Chat History + Tools Menu)
   │
   ▼
Ollama checks the query against tool descriptions.
AI says: "Please call get_city_weather with city='Delhi'." (finish_reason = "tool_calls")
   │
   ▼
Python runs: get_city_weather(city="Delhi")
Result from internet: "Delhi: ✨ +23°C"
   │
   ▼
Python adds this result to Chat History with role="tool"
   │
   ▼
[API Call #2] Send updated History (with tool result) to Ollama
   │
   ▼
AI reads the result and says nicely:
"The weather in Delhi is currently 23°C with clear skies!"
```

---

### 4. 🧩 The 4 Conversation Roles (Cheat Sheet)

Until now, we used 3 roles. Today we unlocked the 4th and final role:

| Role | Who uses it? | What is it for? |
| :--- | :--- | :--- |
| **`"system"`** | Developer (You) | Sets the AI's personality, rules, and limits (pinned at index 0). |
| **`"user"`** | Human | The question or prompt typed into the chat. |
| **`"assistant"`** | The AI Model | The AI's spoken reply OR its request to call a tool. |
| **`"tool"`** | Python Program | The raw answer returned by our function (requires `tool_call_id`). |

---

### 5. 💻 Code Walkthrough (Easy & Line-by-Line)

#### Part A: `tools.py` (Our Tool Box)

We keep all tools in a separate file so our code stays clean and organized.

```python
from datetime import datetime
import requests

# Tool 1: Simple function with NO parameters
def get_current_time():
    """Returns the current date and time as a string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Tool 2: Function WITH a parameter (city)
def get_city_weather(city: str):
    """Fetches real-time weather from wttr.in."""
    url = f"https://wttr.in/{city}?format=3"
    response = requests.get(url, timeout=10) # 10 sec safety timeout
    response.raise_for_status()              # Raise error if website fails
    return response.text.strip()
```

##### Describing Tools in JSON (The Menu Sent to AI)
The AI cannot read Python code, so we describe each function in a simple JSON format:

```python
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Returns current local date and time. Use when user asks for time or date.",
            "parameters": {
                "type": "object",
                "properties": {},   # Empty because it needs no inputs
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_city_weather",
            "description": "Returns live weather of a city. Use when user asks for weather or temperature.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "Name of the city (e.g., Delhi, Seattle)"
                    }
                },
                "required": ["city"] # City is mandatory!
            }
        }
    }
]

# Simple dictionary mapping name (string) to real function
FUNCTION_NAME_TO_FUNCTION_MAP = {
    "get_current_time": get_current_time,
    "get_city_weather": get_city_weather
}
```

> [!TIP]
> **Why write good descriptions?**  
> The AI reads the `description` to decide whether to call your tool! If you write a bad description, the AI won't know when to use it.

---

#### Part B: `simple_ai_assistant.py` (The Brain Loop)

Here is how the main loop handles tool calling:

```python
# 1. First Call: Send messages AND the tools menu
response = client.chat.completions.create(
    model=model_name,
    messages=messages,
    tools=TOOLS
)

msg = response.choices[0].message

# 2. Did the AI ask to call a tool?
if msg.tool_calls:
    # Save the AI's tool request in history
    messages.append(msg)

    # Loop over every tool requested (AI can ask for 1 or more)
    for tool_call in msg.tool_calls:
        func_name = tool_call.function.name
        
        # Arguments come as a JSON string: '{"city": "Delhi"}'
        # json.loads() converts it into a Python dictionary: {"city": "Delhi"}
        func_args = json.loads(tool_call.function.arguments or "{}")

        # Find the function and run it!
        fn = FUNCTION_NAME_TO_FUNCTION_MAP[func_name]
        result = fn(**func_args) # Unpacks dictionary into arguments: fn(city="Delhi")

        # Append the tool result to history
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id, # Links result to the specific tool call
            "content": str(result)
        })

    # 3. Second Call: Send updated history back to AI for final answer
    second_response = client.chat.completions.create(
        model=model_name,
        messages=messages
    )
    final_reply = second_response.choices[0].message.content or ""
    print("Assistant: " + final_reply)
    messages.append({"role": "assistant", "content": final_reply})

else:
    # Normal chat (no tools needed)
    reply = msg.content or ""
    print("Assistant: " + reply)
    messages.append({"role": "assistant", "content": reply})
```

---

### 6. 🔍 Two Special Python Tricks Explained

#### Trick 1: `json.loads(...)`
- **What it does:** The AI sends arguments as a plain text string: `'{"city": "Seattle"}'`.
- **Why we need it:** Python cannot read keys from a string. `json.loads()` converts that text into a real Python dictionary: `{"city": "Seattle"}`.

#### Trick 2: The Double Star `**` (Dictionary Unpacking)
- **What it does:** If you have `args = {"city": "Seattle"}`, calling `fn(**args)` turns into:
  `fn(city="Seattle")`.
- **Why we need it:** We don't have to write custom `if/else` checks for every single parameter. Python automatically unpacks any dictionary keys into function arguments!

---

### 7. ⚠️ Common Mistakes & Traps to Avoid

1. **Thinking the AI runs the code:**  
   ❌ *Mistake:* Assuming Ollama connects to the internet.  
   ✅ *Truth:* Ollama only outputs the text `"get_city_weather"`. Your Python code calls the internet.

2. **Forgetting `json.loads()`:**  
   ❌ *Mistake:* Passing `tool_call.function.arguments` directly to the function.  
   ✅ *Truth:* It is a string, not a dictionary. Always parse it with `json.loads()`.

3. **Missing `tool_call_id`:**  
   ❌ *Mistake:* Forgetting to include `"tool_call_id": tool_call.id` in the tool message.  
   ✅ *Truth:* The API will crash with an error because it doesn't know which tool call the result belongs to.

4. **Forgetting to append the AI's request:**  
   ❌ *Mistake:* Appending the tool result without first appending `messages.append(msg)`.  
   ✅ *Truth:* History must stay continuous: Request $\rightarrow$ Tool Output $\rightarrow$ Final Answer.

---

### 8. 🎓 Quick Interview Flashcards

**Q1: What is Tool Calling (Function Calling)?**  
> **Answer:** It is a feature where we give the LLM a list of functions. If the LLM needs external data, it pauses and tells our code which function to call and with what arguments. Our code runs the function and gives the result back to the LLM.

**Q2: Why does tool calling require two API calls?**  
> **Answer:**
> - Call #1: Asks the LLM which tool to use.
> - Call #2: Sends the tool's result back so the LLM can write a friendly answer for the user.

**Q3: What does the `**` operator do when calling `fn(**func_args)`?**  
> **Answer:** It is the dictionary unpacking operator. It takes a dictionary like `{"city": "Delhi"}` and passes it as keyword arguments: `fn(city="Delhi")`.

**Q4: What happens if a user asks a normal question like "Tell me a joke"?**  
> **Answer:** The LLM checks its tools menu, sees that no tool is needed, and answers directly with text in Call #1 (`msg.tool_calls` is `None`).

---

### 9. 🧪 Verification & Results

We tested our assistant on an **Intel i3** with `qwen2.5:1.5b`:

| Query | Tool Used | Result |
| :--- | :--- | :--- |
| `"What time is it now?"` | `get_current_time()` | ✅ Answered with live local time. |
| `"What is the weather in Delhi?"` | `get_city_weather(city="Delhi")` | ✅ Queried wttr.in and reported 23°C. |
| `"Tell me a one-sentence tip."` | *None* | ✅ Direct natural language answer. |

---

### 10. 🚀 What's Next? (The Bridge to Phase 5)
Right now, our assistant can only call **one tool round** at a time.  
In real-world AI agents, complex tasks need **loops of reasoning and acting** (e.g., Check weather $\rightarrow$ Check flights $\rightarrow$ Send email).  
This is called the **ReAct pattern** (Reason + Act), which we will explore next!




