"""
Agent 3: Translation Agent
Converts language-agnostic pseudocode into clean, modern Python (or Java) code.
"""

from utils.llm_client import call_llm
from utils.logger import get_logger

logger = get_logger("TranslationAgent")


PYTHON_PROMPT = """You are an expert Python developer. Your task is to translate the provided
pseudocode (Intermediate Representation) into clean, idiomatic, production-quality Python 3 code.

PSEUDOCODE (IR):
```
{pseudocode}
```

ORIGINAL PROGRAM DOCUMENTATION (for context):
{documentation}

Requirements for the Python code:
1. Use modern Python 3.10+ syntax and idioms
2. Use type hints on all functions and variables where appropriate
3. Organize code into well-named functions or classes that reflect the original structure
4. Replace legacy file I/O patterns with Pythonic equivalents (open(), with statements, etc.)
5. Replace fixed-length string operations with proper Python string methods
6. Use meaningful variable names (not single letters, not COBOL-style all-caps)
7. Add clear docstrings to all classes and functions
8. Add inline comments for any non-obvious business logic
9. Handle errors with try/except where appropriate
10. Preserve ALL business logic exactly - do not simplify or skip any condition or calculation

OUTPUT ONLY THE PYTHON CODE. No markdown fences, no explanation outside of code comments.
Start your output with: # Translated by NewGenCode from legacy source
"""

JAVA_PROMPT = """You are an expert Java developer. Your task is to translate the provided
pseudocode (Intermediate Representation) into clean, idiomatic, production-quality Java 17+ code.

PSEUDOCODE (IR):
```
{pseudocode}
```

ORIGINAL PROGRAM DOCUMENTATION (for context):
{documentation}

Requirements for the Java code:
1. Use Java 17+ features where applicable (records, switch expressions, etc.)
2. Organize code into a proper class with a main() method and helper methods
3. Use meaningful variable and method names (camelCase, descriptive)
4. Add Javadoc comments to all public methods and the class
5. Add inline comments for non-obvious business logic
6. Use proper Java types (int, double, String, boolean, etc.)
7. Replace legacy file I/O with java.nio or java.io equivalents
8. Handle exceptions with try-catch where appropriate
9. Preserve ALL business logic exactly - do not simplify or skip any condition or calculation

OUTPUT ONLY THE JAVA CODE. No markdown fences, no explanation outside of comments.
Start your output with: // Translated by NewGenCode from legacy source
"""

C_PROMPT = """You are an expert C developer. Your task is to translate the provided
pseudocode (Intermediate Representation) into clean, modern, production-quality C11 code.

PSEUDOCODE (IR):
```
{pseudocode}
```

ORIGINAL PROGRAM DOCUMENTATION (for context):
{documentation}

Requirements for the C code:
1. Use C11 standard features and idioms
2. Include all necessary standard headers (stdio.h, stdlib.h, string.h, math.h, etc.)
3. Organize code into well-named functions with clear signatures
4. Use meaningful variable and function names (snake_case, descriptive)
5. Add block comments (/* */) to all functions describing purpose, parameters, and return value
6. Add inline comments for non-obvious business logic
7. Use proper C types (int, double, float, char, size_t, etc.)
8. Use proper memory management — malloc/free where needed, avoid leaks
9. Handle errors and edge cases (NULL checks, bounds checks, division by zero)
10. Preserve ALL business logic exactly — do not simplify or skip any condition or calculation

OUTPUT ONLY THE C CODE. No markdown fences, no explanation outside of code comments.
Start your output with: // Translated by NewGenCode from legacy source
"""

CPP_PROMPT = """You are an expert C++ developer. Your task is to translate the provided
pseudocode (Intermediate Representation) into clean, modern, production-quality C++17 code.

PSEUDOCODE (IR):
```
{pseudocode}
```

ORIGINAL PROGRAM DOCUMENTATION (for context):
{documentation}

Requirements for the C++ code:
1. Use C++17 standard features and idioms
2. Include all necessary standard headers (<iostream>, <string>, <vector>, <stdexcept>, etc.)
3. Organize code using classes or structs where appropriate, with a main() entry point
4. Use meaningful variable, function, and class names (camelCase for methods, PascalCase for classes)
5. Add Doxygen-style comments (///) to all classes, methods, and functions
6. Add inline comments for non-obvious business logic
7. Use modern C++ types: std::string instead of char*, std::vector instead of raw arrays
8. Prefer RAII and smart pointers (std::unique_ptr, std::shared_ptr) over raw pointers
9. Handle errors with exceptions (std::runtime_error, etc.) where appropriate
10. Preserve ALL business logic exactly — do not simplify or skip any condition or calculation

OUTPUT ONLY THE C++ CODE. No markdown fences, no explanation outside of code comments.
Start your output with: // Translated by NewGenCode from legacy source
"""


class TranslationAgent:
    """
    Translates pseudocode IR into modern Python or Java code.
    This is the third and final agent in the NewGenCode pipeline.
    """

    PROMPTS = {
        "python": PYTHON_PROMPT,
        "java": JAVA_PROMPT,
        "c": C_PROMPT,
        "cpp": CPP_PROMPT,
    }

    # Output file extensions per target language
    EXTENSIONS = {
        "python": "py",
        "java": "java",
        "c": "c",
        "cpp": "cpp",
    }

    def __init__(self):
        logger.info("TranslationAgent initialized")

    def translate(self, pseudocode: str, documentation: str, target_language: str = "python") -> str:
        """
        Translate pseudocode into the target modern language.

        Args:
            pseudocode: The language-agnostic IR from IRGeneratorAgent
            documentation: The documentation from AnalyzerAgent (for context)
            target_language: 'python' or 'java'

        Returns:
            Translated source code as a string
        """
        target = target_language.lower()
        if target not in self.PROMPTS:
            raise ValueError(f"Unsupported target language: {target_language}. Choose 'python', 'java', 'c', or 'cpp'.")

        logger.info(f"Translating pseudocode to {target.capitalize()}...")

        prompt = self.PROMPTS[target].format(
            pseudocode=pseudocode,
            documentation=documentation
        )

        logger.info("Sending to Gemini for translation...")
        translated_code = call_llm(prompt, temperature=0.15)

        # Strip accidental markdown fences if Gemini adds them
        translated_code = self._clean_output(translated_code)

        logger.info(f"Translation complete. Output: {len(translated_code)} characters")
        return translated_code

    def _clean_output(self, code: str) -> str:
        """Remove any accidental markdown code fences from LLM output."""
        lines = code.split("\n")
        cleaned = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("```"):
                continue
            cleaned.append(line)
        return "\n".join(cleaned).strip()
