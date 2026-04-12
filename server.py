"""
NewGenCode FastAPI Backend Server
Full 5-agent pipeline exposed as a REST API for the React frontend.
"""

import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from agents.analyzer import LegacyCodeAnalyzerAgent
from agents.ir_generator import IRGeneratorAgent
from agents.translator import TranslationAgent
from agents.debugger import DebuggerAgent
from agents.documentation import DocumentationAgent
from utils.file_handler import detect_language
from utils.logger import get_logger

logger = get_logger("NewGenCode-API")

app = FastAPI(
    title="NewGenCode API",
    description="AI-Driven 5-Agent Legacy Code Modernization Pipeline",
    version="2.0.0"
)

# ── PDF export router (must come AFTER app is created) ──────────────────────
from pdf_export import router as pdf_router
app.include_router(pdf_router)
# ────────────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "NewGenCode API is running", "version": "2.0.0", "agents": 5}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/analyze")
async def analyze(
    file: UploadFile = File(...),
    target_language: str = Form(default="python")
):
    filename = file.filename or "upload.cbl"
    ext = os.path.splitext(filename)[1].lower()
    allowed = {".cbl", ".cob", ".cpy", ".f", ".for", ".f90", ".f95", ".f03"}

    if ext not in allowed:
        raise HTTPException(status_code=400, detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(sorted(allowed))}")

    if target_language not in ("python", "java", "c", "cpp"):
        raise HTTPException(status_code=400, detail="target_language must be 'python', 'java', 'c', or 'cpp'")

    content = await file.read()
    try:
        code_text = content.decode("utf-8")
    except UnicodeDecodeError:
        code_text = content.decode("latin-1")

    source_language = detect_language(filename)
    if source_language == "unknown":
        source_language = "cobol"

    base_name = os.path.splitext(filename)[0]
    logger.info(f"File: {filename} | Source: {source_language} | Target: {target_language}")

    try:
        logger.info("[Agent 1] Analyzer running...")
        analyzer = LegacyCodeAnalyzerAgent()
        analysis = analyzer.analyze(code_text, source_language)
        logger.info("[Agent 1] Complete")

        logger.info("[Agent 2] IR Generator running...")
        ir_agent = IRGeneratorAgent()
        pseudocode = ir_agent.generate(code_text, analysis, source_language)
        logger.info("[Agent 2] Complete")

        logger.info("[Agent 3] Translator running...")
        translator = TranslationAgent()
        translated_code = translator.translate(pseudocode, analysis, target_language)
        logger.info("[Agent 3] Complete")

        logger.info("[Agent 4] Debugger running...")
        debugger = DebuggerAgent()
        debug_result = debugger.debug(
            translated_code=translated_code,
            pseudocode=pseudocode,
            source_language=source_language,
            target_language=target_language
        )
        review_report = debug_result["review_report"]
        corrected_code = debug_result["corrected_code"]
        logger.info("[Agent 4] Complete")

        logger.info("[Agent 5] Documentation Agent running...")
        doc_agent = DocumentationAgent()
        full_documentation = doc_agent.document(
            pseudocode=pseudocode,
            translated_code=corrected_code,
            review_report=review_report,
            source_language=source_language,
            target_language=target_language,
            filename=base_name
        )
        logger.info("[Agent 5] Complete")

        logger.info("All 5 agents complete.")

        return JSONResponse({
            "success": True,
            "filename": filename,
            "source_language": source_language,
            "target_language": target_language,
            "analysis":           analysis,
            "pseudocode":         pseudocode,
            "translated_code":    translated_code,
            "corrected_code":     corrected_code,
            "full_documentation": full_documentation,
        })

    except EnvironmentError as e:
        raise HTTPException(status_code=500, detail=f"Configuration error: {str(e)}")
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)