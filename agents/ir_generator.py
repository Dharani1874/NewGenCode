"""
Agent 2: IR Generator Agent
Converts legacy code + documentation into language-agnostic pseudocode (Intermediate Representation).
This IR acts as a clean, readable bridge between the legacy code and the modern translation.
"""

from utils.llm_client import call_llm
from utils.logger import get_logger

logger = get_logger("IRGeneratorAgent")


IR_PROMPT = """You are an expert software architect. Your task is to create a clear,
language-agnostic Intermediate Representation (IR) / pseudocode from the provided legacy code and its documentation.

SOURCE LANGUAGE: {language}

ORIGINAL {language} CODE:
```
{code}
```

DOCUMENTATION ANALYSIS:
{documentation}

Your goal is to produce structured pseudocode that:
1. Captures ALL business logic faithfully - nothing should be lost
2. Is completely independent of {language} syntax
3. Is readable by any developer regardless of their background
4. Preserves the exact order of operations
5. Clearly marks: INPUTS, OUTPUTS, CONDITIONS, LOOPS, CALCULATIONS, and FUNCTION CALLS

Use the following pseudocode conventions:

- PROGRAM <name>
- INPUT: <variable> AS <type>
- OUTPUT: <variable> AS <type>
- SET <variable> = <value>
- IF <condition> THEN / ELSE IF / ELSE / END IF
- FOR <variable> FROM <start> TO <end> DO / END FOR
- WHILE <condition> DO / END WHILE
- CALL <function>(<args>) RETURNING <result>
- RETURN <value>
- PRINT <value>
- FUNCTION <name>(<params>) RETURNS <type>: / END FUNCTION
- COMMENT: <explanation>

Be exhaustive. Do not summarize or skip any logic. Every branch, every calculation, every loop must appear in the pseudocode.

OUTPUT ONLY THE PSEUDOCODE. No additional explanation outside of the pseudocode itself.
"""


class IRGeneratorAgent:
    """
    Converts legacy code + documentation into language-agnostic pseudocode (IR).
    This is the second agent in the NewGenCode pipeline.
    """

    def __init__(self):
        logger.info("IRGeneratorAgent initialized")

    def generate(self, code: str, documentation: str, language: str = "COBOL") -> str:
        """
        Generate pseudocode IR from legacy code and documentation.

        Args:
            code: The original legacy source code
            documentation: The Markdown documentation from the Analyzer Agent
            language: The source language

        Returns:
            Language-agnostic pseudocode string
        """
        lang_upper = language.upper()
        logger.info(f"Generating IR from {lang_upper} code...")

        prompt = IR_PROMPT.format(
            language=lang_upper,
            code=code,
            documentation=documentation
        )

        logger.info("Sending to Gemini for IR generation...")
        pseudocode = call_llm(prompt, temperature=0.1)

        logger.info(f"IR generation complete. Pseudocode: {len(pseudocode)} characters")
        return pseudocode
