"""
PDF export route — add this to your existing FastAPI server.py

Install dependency (once):
    pip install reportlab

Usage:
    POST /api/export-pdf
    Body (JSON): { "markdown": "...", "filename": "payroll_demo" }
    Returns: PDF file download
"""

import io
import re
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Preformatted, HRFlowable
)
from reportlab.lib.enums import TA_LEFT

router = APIRouter()


# ── Colour palette (matches the warm UI theme) ──────────────────────────────
WARM_DARK   = colors.HexColor("#1c1612")
WARM_MID    = colors.HexColor("#5c4f3d")
WARM_MUTED  = colors.HexColor("#a8937a")
WARM_ACCENT = colors.HexColor("#b45309")
CODE_BG     = colors.HexColor("#2d2418")
CODE_FG     = colors.HexColor("#f0e6d3")
PAGE_BG     = colors.HexColor("#f0e9dc")
HR_COLOR    = colors.HexColor("#e8e0d4")


def _build_styles():
    base = getSampleStyleSheet()

    styles = {
        "h1": ParagraphStyle(
            "H1",
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=26,
            textColor=WARM_DARK,
            spaceAfter=10,
        ),
        "h2": ParagraphStyle(
            "H2",
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=18,
            textColor=WARM_ACCENT,
            spaceBefore=14,
            spaceAfter=4,
        ),
        "h3": ParagraphStyle(
            "H3",
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=16,
            textColor=WARM_MID,
            spaceBefore=10,
            spaceAfter=4,
        ),
        "body": ParagraphStyle(
            "Body",
            fontName="Helvetica",
            fontSize=10,
            leading=15,
            textColor=WARM_DARK,
            spaceAfter=6,
        ),
        "bullet": ParagraphStyle(
            "Bullet",
            fontName="Helvetica",
            fontSize=10,
            leading=15,
            textColor=WARM_DARK,
            leftIndent=14,
            bulletIndent=4,
            spaceAfter=3,
        ),
        "italic": ParagraphStyle(
            "Italic",
            fontName="Helvetica-Oblique",
            fontSize=9,
            leading=13,
            textColor=WARM_MUTED,
            spaceAfter=6,
        ),
        "code": ParagraphStyle(
            "Code",
            fontName="Courier",
            fontSize=8.5,
            leading=13,
            textColor=CODE_FG,
            backColor=CODE_BG,
            leftIndent=10,
            rightIndent=10,
            spaceAfter=8,
            spaceBefore=4,
        ),
    }
    return styles


def _escape(text: str) -> str:
    """Escape XML special chars for ReportLab Paragraph."""
    return (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
    )


def markdown_to_flowables(md: str, styles: dict):
    """
    Lightweight Markdown → ReportLab flowables converter.
    Handles: # headings, **bold**, *italic*, `inline code`,
             fenced code blocks, bullet lists, --- dividers, plain paragraphs.
    """
    flowables = []
    lines = md.splitlines()
    i = 0

    while i < len(lines):
        line = lines[i]

        # Fenced code block  ```...```
        if line.strip().startswith("```"):
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            code_text = "\n".join(code_lines)
            flowables.append(Preformatted(code_text, styles["code"]))
            i += 1
            continue

        # HR  ---
        if re.match(r"^-{3,}$", line.strip()):
            flowables.append(Spacer(1, 4))
            flowables.append(HRFlowable(width="100%", thickness=0.5, color=HR_COLOR))
            flowables.append(Spacer(1, 4))
            i += 1
            continue

        # Headings
        h_match = re.match(r"^(#{1,3})\s+(.*)", line)
        if h_match:
            level = len(h_match.group(1))
        style_key = {1: "h1", 2: "h2", 3: "h3"}.get(level) if h_match else None
        if h_match and style_key:
            text = _inline_format(_escape(h_match.group(2)), styles)
            flowables.append(Paragraph(text, styles[style_key]))
            i += 1
            continue

        # Bullet / list item
        bullet_match = re.match(r"^[\-\*]\s+(.*)", line)
        if bullet_match:
            text = _inline_format(_escape(bullet_match.group(1)), styles)
            flowables.append(Paragraph(f"&bull; {text}", styles["bullet"]))
            i += 1
            continue

        # Numbered list item
        num_match = re.match(r"^\d+\.\s+(.*)", line)
        if num_match:
            text = _inline_format(_escape(num_match.group(1)), styles)
            flowables.append(Paragraph(f"&bull; {text}", styles["bullet"]))
            i += 1
            continue

        # Italic-only line (e.g. *Generated by ...*)
        if line.strip().startswith("*") and line.strip().endswith("*") and not line.strip().startswith("**"):
            inner = line.strip()[1:-1]
            flowables.append(Paragraph(_escape(inner), styles["italic"]))
            i += 1
            continue

        # Blank line → small spacer
        if line.strip() == "":
            flowables.append(Spacer(1, 5))
            i += 1
            continue

        # Plain paragraph
        text = _inline_format(_escape(line), styles)
        flowables.append(Paragraph(text, styles["body"]))
        i += 1

    return flowables


def _inline_format(text: str, styles) -> str:
    """Convert **bold**, *italic*, `code` inline markers to ReportLab XML."""
    # Bold
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    # Italic (single *)
    text = re.sub(r"\*(.+?)\*", r"<i>\1</i>", text)
    # Inline code
    text = re.sub(
        r"`(.+?)`",
        r'<font name="Courier" color="#b45309">\1</font>',
        text,
    )
    return text


def build_pdf(markdown: str, title: str) -> bytes:
    """Convert Markdown string to PDF bytes."""
    buf = io.BytesIO()

    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=22 * mm,
        bottomMargin=22 * mm,
        title=title,
        author="NewGenCode 5-Agent Pipeline",
    )

    styles = _build_styles()
    story = markdown_to_flowables(markdown, styles)

    doc.build(story)
    return buf.getvalue()


# ── Request model ────────────────────────────────────────────────────────────

class ExportRequest(BaseModel):
    markdown: str
    filename: str = "documentation"


# ── Route ────────────────────────────────────────────────────────────────────

@router.post("/api/export-pdf")
async def export_pdf(req: ExportRequest):
    """
    Convert Markdown documentation to a styled PDF and return it
    as a file download.
    """
    pdf_bytes = build_pdf(req.markdown, req.filename)
    safe_name = re.sub(r"[^\w\-]", "_", req.filename) or "documentation"

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{safe_name}.pdf"',
            "Content-Length": str(len(pdf_bytes)),
        },
    )


# ── Wire up in server.py ─────────────────────────────────────────────────────
# In your existing server.py, add these two lines:
#
#   from pdf_export import router as pdf_router
#   app.include_router(pdf_router)