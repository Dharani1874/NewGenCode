"""
NewGenCode - AI-Driven Multi-Agent System for Legacy Code Modernization
Main entry point
"""

import os
import sys
import argparse
from dotenv import load_dotenv
load_dotenv()  # Load GEMINI_API_KEY from .env file
from agents.analyzer import LegacyCodeAnalyzerAgent
from agents.ir_generator import IRGeneratorAgent
from agents.translator import TranslationAgent
from utils.file_handler import read_file, write_file, detect_language
from utils.logger import get_logger

logger = get_logger("NewGenCode")


def run_pipeline(input_file: str, target_language: str = "python", output_dir: str = "output"):
    """
    Run the full NewGenCode multi-agent pipeline.

    Args:
        input_file: Path to the legacy source code file
        target_language: Target language for translation (default: python)
        output_dir: Directory to save output files
    """
    logger.info("=" * 60)
    logger.info("  NewGenCode - Legacy Code Modernization System")
    logger.info("=" * 60)

    # --- Load input ---
    logger.info(f"Loading file: {input_file}")
    legacy_code = read_file(input_file)
    source_language = detect_language(input_file)
    logger.info(f"Detected language: {source_language.upper()}")

    os.makedirs(output_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(input_file))[0]

    # --- Agent 1: Analyzer ---
    logger.info("\n[AGENT 1] Legacy Code Analyzer Agent")
    logger.info("-" * 40)
    analyzer = LegacyCodeAnalyzerAgent()
    documentation = analyzer.analyze(legacy_code, source_language)
    doc_path = os.path.join(output_dir, f"{base_name}_documentation.md")
    write_file(doc_path, documentation)
    logger.info(f"Documentation saved → {doc_path}")

    # --- Agent 2: IR Generator ---
    logger.info("\n[AGENT 2] IR Generator Agent")
    logger.info("-" * 40)
    ir_agent = IRGeneratorAgent()
    pseudocode = ir_agent.generate(legacy_code, documentation, source_language)
    ir_path = os.path.join(output_dir, f"{base_name}_pseudocode.txt")
    write_file(ir_path, pseudocode)
    logger.info(f"Pseudocode (IR) saved → {ir_path}")

    # --- Agent 3: Translation ---
    logger.info("\n[AGENT 3] Translation Agent")
    logger.info("-" * 40)
    translator = TranslationAgent()
    modern_code = translator.translate(pseudocode, documentation, target_language)
    ext = "py" if target_language == "python" else "java"
    code_path = os.path.join(output_dir, f"{base_name}_translated.{ext}")
    write_file(code_path, modern_code)
    logger.info(f"Translated code saved → {code_path}")

    # --- Done ---
    logger.info("\n" + "=" * 60)
    logger.info("  Pipeline Complete!")
    logger.info(f"  Output files saved in: {output_dir}/")
    logger.info("=" * 60)

    return {
        "documentation": doc_path,
        "pseudocode": ir_path,
        "translated_code": code_path
    }


def main():
    parser = argparse.ArgumentParser(
        description="NewGenCode: Modernize legacy COBOL/FORTRAN code using AI agents"
    )
    parser.add_argument("input_file", help="Path to legacy source code file (.cbl, .cob, .f, .for, .f90)")
    parser.add_argument(
        "--target", "-t",
        choices=["python", "java"],
        default="python",
        help="Target language for translation (default: python)"
    )
    parser.add_argument(
        "--output", "-o",
        default="output",
        help="Output directory (default: ./output)"
    )

    args = parser.parse_args()

    if not os.path.exists(args.input_file):
        logger.error(f"File not found: {args.input_file}")
        sys.exit(1)

    results = run_pipeline(args.input_file, args.target, args.output)
    print(f"\nAll outputs saved to: {args.output}/")


if __name__ == "__main__":
    main()
