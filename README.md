# ⚡ Dev Buddy — AI Agentic App Generator

Dev Buddy is an agentic AI system that generates complete web applications from a single text prompt. Describe the app you want, choose your preferred LLM provider, and three specialized AI agents collaborate to plan, architect, and code it autonomously — with a live preview in your browser.

## Demo
UI

![Dev Buddy UI](demo_image/start.png)

Generated App Preview
![Generated App Preview](demo_image/final.png)

## How It Works

The system uses a **LangGraph StateGraph** to orchestrate three agents in sequence:

1. **Planner Agent** — Converts your text prompt into a structured project plan (app name, tech stack, features, files to create)
2. **Architect Agent** — Converts the plan into ordered implementation steps with full context and dependencies
3. **Coder Agent** — A ReAct agent that iterates through each step and writes the actual code files using file I/O tools

```
User Prompt → Planner → Architect → Coder (loop per step) → Generated App
```

Each generated app is saved to its own uniquely-named subfolder under `generated_project/` and is instantly previewable and downloadable from the UI.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Agent Orchestration | LangGraph StateGraph |
| LLM Providers | Google Gemini, Groq, Ollama |
| LangChain Integrations | `langchain-google-genai`, `langchain-groq`, `langchain-ollama` |
| Backend | FastAPI + Uvicorn |
| Frontend | Vanilla HTML / CSS / JavaScript |
| Data Validation | Pydantic v2 |
| Package Manager | `uv` (or `pip`) |

---

## Features

- **Multi-provider LLM support** — switch between Gemini, Groq, and Ollama from the UI
- **Dynamic model selection** — models are fetched live from each provider's API
- **Single prompt to full working web app** — HTML, CSS, and JS generated end-to-end
- **Real-time generation logs** — streamed status updates while agents work
- **Live preview** — generated app rendered instantly in an embedded iframe
- **One-click download** — download the entire generated project as a `.zip` archive
- **Isolated project folders** — each generation run gets its own subfolder (slug-based, collision-safe)
- **Safe file I/O** — all writes are sandboxed to the `generated_project/` directory
- **CLI support** — run the agent directly from the terminal with `main.py`

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/SamarthKuchya/dev-buddy.git
cd dev-buddy
```

### 2. Install dependencies

With `uv` (recommended):
```bash
uv sync
```

Or with `pip`:
```bash
pip install -e .
```

### 3. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and fill in the keys for the provider(s) you want to use:

```env
# Required for Gemini
GEMINI_API_KEY=your_gemini_api_key

# Required for Groq
GROQ_API_KEY=your_groq_api_key

# Optional — only if Ollama is not on the default localhost:11434
OLLAMA_BASE_URL=http://localhost:11434
```

- Get a free Gemini API key at: https://aistudio.google.com/app/apikey
- Get a free Groq API key at: https://console.groq.com/keys
- Ollama runs locally — install it from: https://ollama.com

### 4. Run the server

```bash
python server.py
```

Open **http://localhost:8000** in your browser.

---

## Usage

1. Select your **LLM provider** (Gemini, Groq, or Ollama) from the dropdown
2. Select the **model** — the list is fetched live from the chosen provider (Use `openai/gpt-oss-120b` by groq for better results)
3. Enter a description of the app you want to build
4. Click **Generate App**
5. Watch the console as agents plan, architect, and code your app
6. **Preview** the generated app live in the right panel
7. Click **Download** to save the project as a `.zip`

### Example Prompts

- `A todo list app with add, complete, and delete functionality`
- `A simple calculator with a clean dark theme`
- `A weather dashboard with city search and temperature display`
- `A personal expense tracker with a chart showing spending by category`

---

## Project Structure

```
app-builder/
├── server.py              # FastAPI backend — API routes and static file serving
├── main.py                # CLI entry point
├── pyproject.toml         # Project metadata and dependencies
├── .env                   # API keys
├── agent/
│   ├── graph.py           # LangGraph StateGraph — agent orchestration & run_agent()
│   ├── llm_providers.py   # Multi-provider LLM factory (Gemini / Groq / Ollama)
│   ├── prompts.py         # System prompts for each agent role
│   ├── states.py          # Pydantic state models (Plan, TaskPlan, CoderState)
│   └── tools.py           # Sandboxed file I/O tools for the coder ReAct agent
├── frontend/
│   ├── index.html         # Main UI — provider/model selector, prompt input, preview
│   ├── script.js          # Status polling, live logs, download button logic
│   └── styles.css         # Dark theme styling
└── generated_project/     # Output directory — one subfolder per generated app
```

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/generate` | Start a new generation task. Returns a `task_id`. |
| `GET` | `/status/{task_id}` | Poll task status, logs, `app_name`, and `project_dir`. |
| `GET` | `/download/{folder_name}` | Download the project folder as a `.zip` archive. |
| `GET` | `/api/providers/{provider}/models` | Fetch available models for `gemini`, `groq`, or `ollama`. |
| `GET` | `/generated_project/{folder}/...` | Serve generated project files (static). |

### `/generate` Request Body

```json
{
  "prompt":   "A todo list app with dark theme",
  "provider": "gemini",
  "model":    "gemini-2.5-flash"
}
```

### `/status/{task_id}` Response

```json
{
  "status":      "running | done | error",
  "logs":        ["⚙ Starting...", "🏷 App name decided: \"Todo App\""],
  "app_name":    "Todo App",
  "project_dir": "/path/to/generated_project/todo-app"
}
```

---

## LLM Providers

| Provider | Key Required | Model Discovery | Notes |
|----------|-------------|-----------------|-------|
| **Gemini** | `GEMINI_API_KEY` | Static list | Supports `gemini-2.5-pro`, `gemini-2.5-flash`, `gemini-2.0-flash`, `gemini-1.5-pro` |
| **Groq** | `GROQ_API_KEY` | Live from Groq API | Fast inference, free tier available |
| **Ollama** | None | Live from local `/api/tags` | Fully local, requires Ollama running on `localhost:11434` |

---

## Notes

- Generated apps are plain **HTML / CSS / JS** — no build step or Node.js required
- Each run creates an isolated subfolder under `generated_project/` — previous generations are never overwritten
- The `generated_project/` directory is gitignored by default
- Ollama must be running locally before selecting it as a provider

---

## Author

Samarth Kumar Kuchya — [LinkedIn](https://www.linkedin.com/in/samarth-kuchya/) | [GitHub](https://github.com/SamarthKuchya)
