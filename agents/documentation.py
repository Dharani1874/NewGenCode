"""
agents/documentation.py — Agent 5: Documentation Agent
Generates a concise summary report for the modernized code.
"""

from utils.llm_client import call_llm

PROMPT = """You are a technical writer. Write a short, clean documentation report.

Original Language: {source_language}
Target Language: {target_language}

PSEUDOCODE:
{pseudocode}

FINAL CODE:
{translated_code}

DEBUG REPORT:
{review_report}

Write a brief report with ONLY these 4 sections (2-3 lines each, no fluff):

## Overview
What this program does in plain English.

## Key Logic
The main business rules and calculations preserved from the original code.

## Debug Summary
Issues found and fixed (or "No issues found" if clean).

## How to Run
One or two lines on how to execute the translated code.
"""


def document(
    pseudocode: str,
    translated_code: str,
    review_report: str,
    source_language: str = "COBOL",
    target_language: str = "python",
) -> str:
    prompt = PROMPT.format(
        source_language=source_language.upper(),
        target_language=target_language.capitalize(),
        pseudocode=pseudocode,
        translated_code=translated_code,
        review_report=review_report,
    )
    return call_llm(prompt, temperature=0.1)