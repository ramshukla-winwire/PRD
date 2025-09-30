import os

def load_prompt(prompt_file: str) -> str:
    base_path = os.path.join(os.path.dirname(__file__), "..", "prompts")
    full_path = os.path.abspath(os.path.join(base_path, prompt_file))
    with open(full_path, "r", encoding="utf-8") as file:
        return file.read()
