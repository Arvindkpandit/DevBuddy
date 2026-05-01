import pathlib
import subprocess
from typing import Tuple
from langchain_core.tools import tool

_project_root = pathlib.Path.cwd() / "generated_project"

def set_project_root(path: pathlib.Path):
    """Set the project root for the current generation run."""
    global _project_root
    _project_root = path
    _project_root.mkdir(parents=True, exist_ok=True)

def get_project_root() -> pathlib.Path:
    return _project_root

def safe_path_for_project(path: str) -> pathlib.Path:
    root = get_project_root().resolve()
    p = (get_project_root() / path).resolve()
    if root not in p.parents and root != p.parent and root != p:
        raise ValueError(f"Path {p} is not within the project root {root}")
    return p


@tool
def write_file(path: str, content: str) -> str:
    """Writes content to a file at the given path. The path should be relative to the project root."""
    p = safe_path_for_project(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)
    return f"WROTE TO FILE {p}"


@tool
def read_file(path: str) -> str:
    """Reads the content of a file at the given path. The path should be relative to the project root."""
    p = safe_path_for_project(path)
    if not p.exists():
        return ""
    with open(p, "r", encoding="utf-8") as f:
        return f.read()


@tool
def get_current_directory() -> str:
    """Returns the current project root directory."""
    return str(get_project_root())


@tool
def list_files(directory: str = ".") -> str:
    """List files in a directory.

    IMPORTANT: The tool name is EXACTLY 'list_files' (NOT 'repo_browser.list_files', NOT 'browse_files', NOT any other name).

    Args:
        directory: Directory path relative to project root (default: '.')

    Returns:
        Newline-separated list of file paths, or 'No files found' if empty.
    """
    root = get_project_root()
    p = safe_path_for_project(directory)
    if not p.is_dir():
        return f"Error: {p} is not a directory"
    files = [str(f.relative_to(root)) for f in p.rglob("*") if f.is_file()]
    return "\n".join(files) if files else "No files found"


@tool
def run_cmd(cmd: str, cwd: str = None, timeout: int = 30) -> Tuple[int, str, str]:
    """Runs a shell command in the specified directory and returns the result."""
    cwd_dir = safe_path_for_project(cwd) if cwd else get_project_root()
    result = subprocess.run(
        cmd, shell=True, capture_output=True, text=True, cwd=str(cwd_dir), timeout=timeout
    )
    return result.returncode, result.stdout, result.stderr


def init_project_root(project_path: pathlib.Path = None):
    """Initialize (and optionally override) the project root directory."""
    if project_path:
        set_project_root(project_path)
    else:
        get_project_root().mkdir(parents=True, exist_ok=True)
    return f"Initialized project root at {get_project_root()}"