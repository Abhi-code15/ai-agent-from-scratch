📓 AI Agent Engineering Logbook

A practical guide documenting the step-by-step construction of an autonomous AI agent from scratch. Every section covers the concepts introduced, the exact terminal commands run, code walkthroughs with explanations, and the limitations that motivate the next phase.

[Phase 1] - Day 1: Foundation, Local LLM Setup & Interactive Chat Loop

1. What We Built Today

We set up a self-contained local development environment, configured a local Large Language Model (qwen2.5:1.5b) to run offline without paid API keys, and built our first interactive terminal assistant. We established clean engineering habits from line one: decoupling configurations into environment files, isolating project dependencies, and handling user session exits gracefully.

2. Core Concepts: The "Why" Behind Each Decision

Virtual Environment Isolation (.venv)

When you run pip install globally, packages sit in your system-wide Python folder. If Project A needs version 1.0 of a library and Project B needs version 2.0, updating one breaks the other. A virtual environment gives this project its own dedicated Python interpreter and private library folder.

Local Inference via Ollama & Port 11434

Ollama runs open-source LLMs directly on your machine's hardware and exposes an HTTP REST server at http://127.0.0.1:11434/v1. This endpoint mirrors OpenAI's API format, meaning the Python code you write locally will work unchanged with cloud models (like OpenAI, Claude, or Gemini) simply by modifying endpoint settings.

Model Selection: qwen2.5:1.5b vs qwen3:4b

On an Intel Core i3 machine with limited RAM and integrated graphics, a 4B parameter model requires 3+ GB of RAM and runs slowly on the CPU. qwen2.5:1.5b requires under 1 GB of memory, responds significantly faster on standard CPUs, and still natively supports structured JSON outputs and function calling.

Separation of Concerns via .env

Hardcoding URLs, model names, or API keys directly in .py files is unsafe and inflexible. Storing them in a .env file lets you switch models or update environments without editing application logic.

Why python-dotenv is Needed

Python's built-in os library can only read variables already loaded into your computer's active memory (os.environ). It cannot read text files on its own. load_dotenv() parses the .env file on your disk and injects those values into os.environ so os.getenv() can read them.

3. Terminal Commands Reference & Deep Dive

A. Environment & Package Setup

Create the virtual environment:

python -m venv .venv


What it does: Uses Python's built-in venv module to create an isolated folder named .venv containing dedicated copies of Python and pip.

Example: After running this, any library you install stays locked inside this folder instead of modifying your laptop's global Python installation.

Activate the environment (Windows PowerShell):

.\.venv\Scripts\Activate.ps1


What it does: Reconfigures your current terminal session so that running python or pip points directly to .venv\Scripts instead of system Python. You will see (.venv) appear at the start of your terminal prompt.

Install required libraries:

python -m pip install openai python-dotenv


What it does: Installs the official OpenAI client SDK (to talk to OpenAI-compatible endpoints) and python-dotenv (to parse .env files).

Why python -m pip instead of just pip? Running python -m pip forces the terminal to use the pip tool tied directly to your currently active Python executable. This prevents Fatal error in launcher issues if a folder was moved or renamed.

Export dependency manifest:

python -m pip freeze > requirements.txt


What it does: Generates a text file listing every installed library and its exact version number.

Example: Anyone cloning your repo can recreate your exact environment simply by running pip install -r requirements.txt.

B. Local Model Setup (Ollama)

Download and run the model:

ollama run qwen2.5:1.5b


What it does: Connects to Ollama's registry, downloads the weights for the 1.5-billion-parameter Qwen model (~986 MB), and boots an interactive session. Type /bye to exit the model prompt back to your terminal.

Verify downloaded models:

ollama list


What it does: Displays all models stored locally, their unique hash IDs, and file sizes to confirm the model is available offline.

C. Git & GitHub Version Control

Initialize the Git repository:

git init


What it does: Creates a hidden .git folder in your directory, turning your folder into a tracked repository.

Stage files for saving:

git add .


What it does: Gathers all newly created and modified files and places them into the "Staging Area" (the preparation box before taking a snapshot).

Record a commit (snapshot):

git commit -m "feat: implement baseline interactive assistant with dotenv and qwen2.5:1.5b"


What it does: Permanently saves the staged snapshot into your local Git history with a descriptive message explaining what was created.

Set main branch and link to GitHub:

git branch -M main
git remote add origin https://github.com/<your-username>/ai-agent-scratch.git


What it does: Renames your primary branch to main and creates a shortcut named origin pointing to your remote GitHub repository URL.

Upload to GitHub:

git push -u origin main


What it does: Uploads your local commits to GitHub. The -u flag links your local main branch to the remote branch so that in the future, you only need to type git push.

4. Code Implementation & Line-by-Line Walkthrough

Here is the complete source code for simple_ai_assistant.py:

import os
from openai import OpenAI
from dotenv import load_dotenv

# 1. Load key-value pairs from .env into system environment variables
load_dotenv()

# 2. Instantiate OpenAI client pointing to Ollama's local port
client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)

model_name = os.getenv("MODEL")
print(f"--- Assistant Initialized with model: {model_name} ---")
print("Type 'exit', 'quit', or 'bye' to end the session.\n")

# 3. Interactive conversational loop
while True:
    try:
        user_input = input("\nUser: ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\nSession ended.")
        break

    # Graceful exit checking
    if user_input.lower() in ["exit", "quit", "bye", "goodbye"]:
        print("Assistant: Goodbye!")
        break

    # Skip empty input submissions
    if not user_input:
        continue

    # 4. Request completion from local LLM
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "user",
                "content": user_input
            }
        ]
    )

    # 5. Extract text reply from choices array
    reply = response.choices[0].message.content
    print("Assistant: " + reply)


Line-by-Line Breakdown:

load_dotenv(): Reads your .env file on disk. Without this line, os.getenv("BASE_URL") returns None.

client = OpenAI(...): Creates the communication object. By overriding base_url to http://127.0.0.1:11434/v1, the client sends API requests to your local laptop instead of OpenAI's remote cloud servers.

while True:: Keeps the Python program running in memory so you can continue chatting without having to rerun the script for each question.

if user_input.lower() in [...]: Catches common exit words and terminates the loop cleanly using break, preventing an unnecessary call to the model.

client.chat.completions.create(...): Bundles your input into OpenAI's standard payload format and sends it to the LLM.

response.choices[0].message.content: LLM completions return an array of candidate responses called choices. Because we only request one answer, we access item index 0 and retrieve its content string.

5. Identified Limitations (The Bridge to Phase 2)

If you test the assistant with these two prompts:

User: My name is Alex. $\to$ Assistant: "Nice to meet you, Alex!"

User: What is my name? $\to$ Assistant: "I'm sorry, I don't know your name."

The Flaw:
LLMs are completely stateless. They do not possess persistent internal memory of past network requests. In our loop:

messages=[
    {"role": "user", "content": user_input}
]


On every single turn, we overwrite messages with only the newest input. The model never receives the history of what was said previously.
