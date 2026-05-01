import warnings
import os
import json
import re
import pathlib
from dotenv import load_dotenv
from agent.prompts import *
from agent.states import *
from langgraph.constants import END
from langgraph.graph import StateGraph
from agent.tools import write_file, read_file, list_files, get_current_directory, run_cmd, init_project_root, set_project_root
from agent.llm_providers import init_llm
from langgraph.prebuilt import create_react_agent

warnings.filterwarnings("ignore")

load_dotenv()

GENERATED_BASE = pathlib.Path.cwd() / "generated_project"

def _slugify(name: str) -> str:
    """Convert an app name to a safe folder name, e.g. 'My Cool App!' → 'my-cool-app'."""
    slug = name.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)   
    slug = re.sub(r"[\s_]+", "-", slug)     
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug


def _extract_json(text: str) -> dict:
    """ extract JSON from LLM response — strips markdown if present."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*\n?", "", text)
    text = re.sub(r"\n?```\s*$", "", text)
    text = text.strip()
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        return json.loads(text)
    return json.loads(text[start:end + 1])


def build_agent(provider: str = "groq", model: str = "openai/gpt-oss-120b"):
    """
    Build and return a compiled LangGraph agent using the specified provider + model.

    Args:
        provider: 'groq', 'gemini', or 'ollama'
        model:    model name for the chosen provider
    """
    llm = init_llm(provider, model)

    def planner_agent(state: dict) -> dict:
        """
        Converts the user's prompt into a structured Plan.
        Also derives a unique app_name slug and project_dir for this run.
        """
        user_prompt = state["user_prompt"]
        response = llm.invoke(planner_prompt(user_prompt))
        raw = response.content if hasattr(response, "content") else str(response)
        data = _extract_json(raw)
        plan = Plan(**data)

        base_slug = _slugify(plan.name)

        # Handling case for duplicate folder names
        candidate = GENERATED_BASE / base_slug
        counter = 1
        while candidate.exists():
            candidate = GENERATED_BASE / f"{base_slug}-{counter}"
            counter += 1

        project_dir = candidate
        project_dir.mkdir(parents=True, exist_ok=True)

        set_project_root(project_dir)

        return {
            "plan": plan,
            "app_name": plan.name,
            "project_dir": str(project_dir),
        }

    def architect_agent(state: dict) -> dict:
        """Creates TaskPlan from the Plan."""
        plan: Plan = state["plan"]
        response = llm.invoke(architect_prompt(plan=plan.model_dump_json()))
        raw = response.content if hasattr(response, "content") else str(response)
        data = _extract_json(raw)
        task_plan = TaskPlan(**data)
        task_plan.plan = plan
        return {"task_plan": task_plan}

    def coder_agent(state: dict) -> dict:
        """LangGraph tool-using coder agent that implements the task plan."""
        coder_state: CoderState = state.get("coder_state")
        if coder_state is None:
            coder_state = CoderState(task_plan=state["task_plan"], current_step_idx=0)

        steps = coder_state.task_plan.implementation_steps
        if coder_state.current_step_idx >= len(steps):
            return {"coder_state": coder_state, "status": "DONE"}

        current_task = steps[coder_state.current_step_idx]
        existing_content = read_file.run(current_task.file_path)

        user_prompt = (
            f"Task: {current_task.task_description}\n"
            f"File to write: {current_task.file_path}\n"
            f"Existing file content (empty if new file):\n{existing_content}\n\n"
            f"Implement the task fully and save the result using write_file."
        )
        system_prompt = coder_prompt()

        coder_tools = [write_file, read_file, list_files, get_current_directory, run_cmd]
        react_agent = create_react_agent(llm, coder_tools)
        react_agent.invoke({
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt},
            ]
        })

        coder_state.current_step_idx += 1
        return {"coder_state": coder_state}

    graph = StateGraph(dict)
    graph.add_node("planner",   planner_agent)
    graph.add_node("architect", architect_agent)
    graph.add_node("coder",     coder_agent)

    graph.add_edge("planner",   "architect")
    graph.add_edge("architect", "coder")

    graph.add_conditional_edges(
        "coder",
        lambda s: "END" if s.get("status") == "DONE" else "coder",
        {"END": END, "coder": "coder"}
    )

    graph.set_entry_point("planner")
    return graph.compile()


def run_agent(
    user_prompt: str,
    on_state_update,
    provider: str = "groq",
    model: str = "openai/gpt-oss-120b",
) -> dict:
    """
    Runs the agent and calls callback with each state update.

    Returns:
        A dict with 'app_name' and 'project_dir' set by the planner node.
    """
    import uuid
    compiled_agent = build_agent(provider, model)
    thread = {"configurable": {"thread_id": str(uuid.uuid4())}}

    result_meta = {"app_name": None, "project_dir": None}

    try:
        stream = compiled_agent.stream(
            {"user_prompt": user_prompt}, thread, stream_mode="updates"
        )
        for event in stream:
            on_state_update(event)
            # Capture app_name / project_dir from the planner node output
            if "planner" in event:
                planner_out = event["planner"]
                result_meta["app_name"]    = planner_out.get("app_name")
                result_meta["project_dir"] = planner_out.get("project_dir")
    except GeneratorExit:
        raise
    except Exception:
        raise

    return result_meta