"""
Agent 4: Debugger Agent
Reviews the translated modern code, identifies bugs, logical errors,
and syntax issues, then returns a corrected and validated version.
"""

from utils.llm_client import call_llm
from utils.logger import get_logger

logger = get_logger("DebuggerAgent")


DEBUGGER_PROMPT = """You are an expert {target_language} code reviewer and debugger.
Your task is to carefully review the translated {target_language} code below, find any issues,
and return a corrected, fully working version.

ORIGINAL LEGACY LANGUAGE: {source_language}

PSEUDOCODE (IR) — the intended logic:
```
{pseudocode}
```

TRANSLATED {target_language} CODE TO REVIEW:
```
{translated_code}
```

Your job:
1. Check for syntax errors and fix them
2. Check that ALL business logic from the pseudocode is correctly implemented
3. Check for logical errors (wrong conditions, off-by-one errors, wrong operators)
4. Check for missing edge cases (e.g. division by zero, empty inputs)
5. Check variable naming is consistent and meaningful
6. Check that data types are correct
7. Ensure the code will actually run without errors

After your review, produce TWO things:

--- REVIEW REPORT ---
List each issue you found as:
[ISSUE TYPE] Description of problem → How you fixed it

If no issues found, write: No issues found. Code is correct.

--- CORRECTED CODE ---
The full corrected {target_language} code, ready to run.
Start with: # Debugged by NewGenCode Debugger Agent
(or // for Java)

IMPORTANT: Always output both sections even if no bugs were found — still output the full corrected code.
"""


class DebuggerAgent:
    """
    Reviews and debugs the translated modern code.
    Identifies syntax errors, logical bugs, and missing edge cases.
    This is the fourth agent in the NewGenCode pipeline.
    """

    def __init__(self):
        logger.info("DebuggerAgent initialized")

    def debug(
        self,
        translated_code: str,
        pseudocode: str,
        source_language: str = "COBOL",
        target_language: str = "python"
    ) -> dict:
        """
        Review and fix the translated code.

        Args:
            translated_code: The code output from TranslationAgent
            pseudocode: The IR pseudocode (used as reference for intended logic)
            source_language: Original legacy language
            target_language: The modern language being debugged

        Returns:
            dict with keys: 'review_report' and 'corrected_code'
        """
        logger.info(f"Debugging {target_language} code ({len(translated_code)} chars)...")

        prompt = DEBUGGER_PROMPT.format(
            target_language=target_language.capitalize(),
            source_language=source_language.upper(),
            pseudocode=pseudocode,
            translated_code=translated_code
        )

        logger.info("Sending to Gemini for debugging...")
        response = call_llm(prompt, temperature=0.1)

        # Parse the two sections from response
        review_report, corrected_code = self._parse_response(response, translated_code)

        logger.info(f"Debugging complete. Issues found: {len(review_report.splitlines())} lines in report")
        return {
            "review_report": review_report,
            "corrected_code": corrected_code
        }

    def _parse_response(self, response: str, fallback_code: str) -> tuple:
        """Split the LLM response into review report and corrected code."""
        review_report = ""
        corrected_code = ""

        if "--- REVIEW REPORT ---" in response and "--- CORRECTED CODE ---" in response:
            parts = response.split("--- CORRECTED CODE ---")
            review_part = parts[0].replace("--- REVIEW REPORT ---", "").strip()
            code_part = parts[1].strip()

            review_report = review_part
            # Strip any accidental markdown fences
            corrected_code = self._strip_fences(code_part)
        else:
            # Fallback: treat whole response as corrected code
            review_report = "Review report could not be parsed separately."
            corrected_code = self._strip_fences(response)

        if not corrected_code.strip():
            corrected_code = fallback_code

        return review_report, corrected_code

    def _strip_fences(self, code: str) -> str:
        """Remove markdown code fences if present."""
        lines = code.split("\n")
        cleaned = [line for line in lines if not line.strip().startswith("```")]
        return "\n".join(cleaned).strip()
