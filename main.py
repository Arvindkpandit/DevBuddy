import argparse
import sys
import traceback
from agent.graph import run_agent

def main():
    parser = argparse.ArgumentParser(description="Dev-Buddy: AI-powered app builder")
    parser.add_argument("--provider", "-p", default="ollama", help="LLM provider: gemini | groq | ollama (default: ollama)")
    parser.add_argument("--model", "-m", default="deepseek-v3.2:cloud", help="Model name for the chosen provider")
    args = parser.parse_args()

    try:
        user_prompt = input("Enter your prompt: ")
        def on_update(event):
            print("[update]", list(event.keys()))
        meta = run_agent(user_prompt, on_update, provider=args.provider, model=args.model)
        print("Done! App:", meta.get("app_name"))
        print("Project folder:", meta.get("project_dir"))
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        traceback.print_exc()
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()