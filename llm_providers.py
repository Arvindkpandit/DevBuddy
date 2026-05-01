import os
import requests
from dotenv import load_dotenv

load_dotenv()

GEMINI_MODELS = [
    "gemini-2.5-pro",
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-pro",
]

def _init_gemini(model: str):
    """Initialize a Google Gemini chat model via langchain-google-genai."""
    from langchain_google_genai import ChatGoogleGenerativeAI

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set in your .env file.")
    return ChatGoogleGenerativeAI(
        model=model,
        google_api_key=api_key,
        temperature=0.1,
    )

def _init_groq(model: str):
    """Initialize a Groq chat model via langchain-groq."""
    from langchain_groq import ChatGroq

    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set in your .env file.")
    return ChatGroq(
        model=model,
        groq_api_key=api_key,
        temperature=0.1,
    )

def _init_ollama(model: str):
    """Initialize an Ollama chat model via langchain-ollama."""
    from langchain_ollama import ChatOllama

    api_key = os.environ.get("OLLAMA_API_KEY", "")
    kwargs = dict(model=model, temperature=0.1)
    if api_key:
        kwargs["api_key"] = api_key
    return ChatOllama(**kwargs)

def init_llm(provider: str, model: str):
    """
    Factory function.  Returns an initialised LangChain chat model.

    Args:
        provider: one of 'gemini', 'groq', 'ollama'
        model:    model name string for the chosen provider
    """
    provider = provider.lower().strip()
    if provider == "gemini":
        return _init_gemini(model)
    elif provider == "groq":
        return _init_groq(model)
    elif provider == "ollama":
        return _init_ollama(model)
    else:
        raise ValueError(f"Unknown provider '{provider}'. Choose from: gemini, groq, ollama")

def get_gemini_models() -> list[str]:
    """Return the static list of supported Gemini models."""
    return GEMINI_MODELS

def get_groq_models() -> list[str]:
    """Fetch available Groq models from the Groq API."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set in your .env file.")

    url = "https://api.groq.com/openai/v1/models"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    data = response.json()
    models = [model["id"] for model in data.get("data", [])]
    return sorted(models)

def get_ollama_models() -> list[str]:
    """Fetch locally available Ollama models from the Ollama tags API."""
    base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
    url = f"{base_url}/api/tags"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        models = [model["name"] for model in data.get("models", [])]
        return sorted(models)
    except requests.exceptions.ConnectionError:
        raise ConnectionError(
            "Could not connect to Ollama. Make sure Ollama is running on localhost:11434"
        )

def get_models_for_provider(provider: str) -> list[str]:
    """Return the model list for a given provider name."""
    provider = provider.lower().strip()
    if provider == "gemini":
        return get_gemini_models()
    elif provider == "groq":
        return get_groq_models()
    elif provider == "ollama":
        return get_ollama_models()
    else:
        raise ValueError(f"Unknown provider '{provider}'.")