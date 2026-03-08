"""
File handling utilities for NewGenCode
"""

import os


LANGUAGE_MAP = {
    ".cbl": "cobol",
    ".cob": "cobol",
    ".cpy": "cobol",
    ".f": "fortran",
    ".for": "fortran",
    ".f90": "fortran",
    ".f95": "fortran",
    ".f03": "fortran",
}


def read_file(filepath: str) -> str:
    """Read a source file and return its contents as a string."""
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def write_file(filepath: str, content: str) -> None:
    """Write content to a file, creating directories as needed."""
    os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else ".", exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)


def detect_language(filepath: str) -> str:
    """Detect the programming language from file extension."""
    ext = os.path.splitext(filepath)[1].lower()
    return LANGUAGE_MAP.get(ext, "unknown")
