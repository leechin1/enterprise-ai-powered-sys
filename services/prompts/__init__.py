"""
Prompt Management Module
Loads prompt templates from text files for AI agents
"""

import os
from pathlib import Path
from typing import List

PROMPTS_DIR = Path(__file__).parent


def load_prompt(filename: str) -> str:
    """
    Load a prompt template from a text file

    Args:
        filename: Name of the prompt file (e.g., 'health_analysis_system_prompt.txt')

    Returns:
        Prompt content as string

    Raises:
        FileNotFoundError: If prompt file doesn't exist
    """
    prompt_path = PROMPTS_DIR / filename

    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

    with open(prompt_path, 'r', encoding='utf-8') as f:
        return f.read()


def load_system_instructions(filename: str) -> List[str]:
    """
    Load system instructions from a text file and split by lines

    Args:
        filename: Name of the instructions file

    Returns:
        List of instruction strings (one per line)
    """
    content = load_prompt(filename)
    # Split by lines and filter out empty lines
    return [line.strip() for line in content.split('\n') if line.strip()]
