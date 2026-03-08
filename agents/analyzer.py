"""
Agent 1: Legacy Code Analyzer Agent
Reads legacy COBOL/FORTRAN code and produces structured documentation
covering purpose, inputs/outputs, and business logic.
"""

from utils.llm_client import call_llm
from utils.logger import get_logger

logger = get_logger("AnalyzerAgent")


ANALYZER_PROMPT = """You are a senior software engineer specializing in legacy systems.
Your task is to analyze the following {language} code and produce clear, structured documentation.

LEGACY {language} CODE:
```
{code}
```

Please produce documentation in the following Markdown format:

# Code Documentation

## 1. Purpose
Provide a clear, concise description of what this program/module does overall.

## 2. Inputs
List all inputs (variables, files, user inputs, parameters) the code receives, with data types where determinable.

## 3. Outputs
List all outputs (printed results, files written, return values, side effects) the code produces.

## 4. Business Logic
Describe the step-by-step logic and rules implemented in the code. Be specific about:
- Calculations and formulas used
- Conditional branches and what they control
- Loops and their purpose
- Any data transformations

## 5. Data Structures
Describe any key variables, arrays, records, or data divisions used.

## 6. Potential Modernization Notes
Note any legacy constructs, patterns, or gotchas that a developer should be aware of when translating this code.

Be thorough and precise. The goal is that a developer who has never seen this code can understand it fully from your documentation alone.
"""


class LegacyCodeAnalyzerAgent:
    """
    Analyzes legacy COBOL/FORTRAN code and generates structured documentation.
    This is the first agent in the NewGenCode pipeline.
    """

    def __init__(self):
        logger.info("LegacyCodeAnalyzerAgent initialized")

    def analyze(self, code: str, language: str = "COBOL") -> str:
        """
        Analyze the provided legacy code and return Markdown documentation.

        Args:
            code: The full source code as a string
            language: The source language (e.g., 'cobol', 'fortran')

        Returns:
            Markdown-formatted documentation string
        """
        lang_upper = language.upper()
        logger.info(f"Analyzing {lang_upper} code ({len(code)} characters)...")

        prompt = ANALYZER_PROMPT.format(
            language=lang_upper,
            code=code
        )

        logger.info("Sending to Gemini for analysis...")
        documentation = call_llm(prompt, temperature=0.1)

        logger.info(f"Analysis complete. Documentation: {len(documentation)} characters")
        return documentation
