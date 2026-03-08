# NewGenCode 🔄
### AI-Driven Multi-Agent System for Legacy Code Modernization

NewGenCode automatically modernizes legacy COBOL and FORTRAN code into clean Python (or Java) using a pipeline of three AI agents powered by Google Gemini.

---

## Architecture

```
Legacy Code (.cbl / .f)
        │
        ▼
┌─────────────────────────┐
│  Agent 1: Analyzer      │  → Reads legacy code
│  LegacyCodeAnalyzerAgent│  → Generates structured documentation
└─────────────────────────┘
        │
        ▼ (documentation)
┌─────────────────────────┐
│  Agent 2: IR Generator  │  → Converts code + docs
│  IRGeneratorAgent       │  → Produces language-agnostic pseudocode
└─────────────────────────┘
        │
        ▼ (pseudocode / IR)
┌─────────────────────────┐
│  Agent 3: Translator    │  → Converts pseudocode
│  TranslationAgent       │  → Produces Python or Java code
└─────────────────────────┘
        │
        ▼
Modern Code (.py / .java)
```

Each agent uses Google Gemini via the free tier API.

---

## Project Structure

```
NewGenCode/
├── main.py                  # Entry point – runs the full pipeline
├── requirements.txt
├── .env.example             # Copy to .env and add your API key
├── .gitignore
│
├── agents/
│   ├── __init__.py
│   ├── analyzer.py          # Agent 1: Legacy Code Analyzer
│   ├── ir_generator.py      # Agent 2: IR / Pseudocode Generator
│   └── translator.py        # Agent 3: Code Translator (Python/Java)
│
├── utils/
│   ├── __init__.py
│   ├── llm_client.py        # Shared Gemini API interface
│   ├── file_handler.py      # File reading, writing, language detection
│   └── logger.py            # Console logging utility
│
├── samples/
│   ├── payroll.cbl          # Sample COBOL: payroll calculator
│   └── grades.f             # Sample FORTRAN: student grade calculator
│
└── output/                  # Generated output files (auto-created)
```

---

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/NewGenCode.git
cd NewGenCode
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Your Gemini API Key

Get a free API key at: https://https://console.groq.com/keys

```bash
cp .env.example .env
# Then edit .env and replace 'your_grok_api_key_here' with your actual key
```

---

## Usage

### Basic Usage (translate a COBOL file to Python)

```bash
python main.py samples/payroll.cbl
```

### Specify Target Language

```bash
python main.py samples/payroll.cbl --target python
python main.py samples/payroll.cbl --target java
```

### Specify Output Directory

```bash
python main.py samples/grades.f --target python --output my_output/
```

---

## Output Files

For each run, three files are generated in the output directory:

| File | Description |
|------|-------------|
| `<name>_documentation.md` | Structured analysis: purpose, I/O, business logic |
| `<name>_pseudocode.txt` | Language-agnostic intermediate representation (IR) |
| `<name>_translated.py` | Final modern Python (or `.java`) code |

---

## Supported Input Formats

| Extension | Language |
|-----------|----------|
| `.cbl`, `.cob`, `.cpy` | COBOL |
| `.f`, `.for`, `.f90`, `.f95`, `.f03` | FORTRAN |

---

## Tech Stack

- **Language**: Python 3.10+
- **LLM**: Google Gemini 1.5 Flash (free tier)
- **Libraries**: `google-generativeai`, `python-dotenv`
- **IDE**: VS Code (recommended)
- **Version Control**: Git + GitHub

---

## Base Papers

| Paper | Focus |
|-------|-------|
| **VAPU** – Autonomous Legacy Code Modernization | Execution-based validation, modernization correctness |
| **RepoTransAgent** – Multi-Agent LLM Framework | Role-based agent coordination for code translation |

NewGenCode combines insights from both: multi-agent design from RepoTransAgent, preservation-focused logic from VAPU.

---

## Future Work (v2+)

- Execution Agent: Run and validate translated code automatically
- Debugging Agent: Fix runtime errors in generated code
- Adversarial Agent: Test edge cases and verify equivalence
- Java translation improvements
- Web UI for non-developers
- Batch processing for large codebases

---

## License

MIT License – see LICENSE file for details.
