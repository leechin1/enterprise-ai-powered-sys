"""
Issues Agent Prompt Management Module
Loads prompt templates from text files for the Issues Agent tools.
"""

from pathlib import Path

PROMPTS_DIR = Path(__file__).parent


def load_issues_prompt(filename: str) -> str:
    """
    Load an issues agent prompt template from a text file.

    Args:
        filename: Name of the prompt file (e.g., 'issues_stage0_sql_generation_prompt.txt')

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


# Pre-load prompts for convenience
def get_sql_generation_prompt() -> str:
    """Load the Stage 0 SQL generation prompt."""
    return load_issues_prompt('issues_stage0_sql_generation_prompt.txt')


def get_issues_analysis_prompt() -> str:
    """Load the Stage 1 issues analysis prompt."""
    return load_issues_prompt('issues_stage1_analysis_prompt.txt')


def get_fixes_prompt() -> str:
    """Load the Stage 2 fixes proposal prompt."""
    return load_issues_prompt('issues_stage2_fixes_prompt.txt')
