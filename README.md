# AI Resume Analyzer — Gemini + Transparent ATS Heuristics

A portfolio-ready Python/Streamlit project inspired by the workflow described in Jyoti Dabass' Medium tutorial on building an AI Resume Analyzer with Google Gemini.

This implementation extends the idea into a **resume-vs-job-description analyzer** with transparent, inspectable scoring plus structured Gemini feedback.

## What it does

- Upload a PDF resume
- Extract resume text, page count, font families, and font sizes with PyMuPDF
- Parse the target job description for frequently occurring role keywords
- Calculate a transparent **ATS-style heuristic score** using:
  - 45% keyword alignment
  - 25% expected resume section coverage
  - 20% evidence of impact (metrics, action-oriented bullets)
  - 10% lightweight formatting checks
- Show matched and missing/underrepresented JD keywords
- Use Google Gemini for structured recruiter-style feedback
- Suggest truthful improvements without inventing candidate experience

> **Important:** The ATS score is a custom project heuristic. It does not claim to reproduce Google, Workday, Greenhouse, Taleo, Lever, or any other commercial/employer ATS scoring algorithm.

## Architecture

```text
Resume PDF ──> PyMuPDF extraction ──> text + font metadata
                                      │
Job Description ──> keyword parser ───┼──> deterministic heuristic scores
                                      │
                                      └──> Gemini structured review
                                                   │
                                                   v
                                          Streamlit dashboard
```

## Project structure

```text
ai-resume-analyzer/
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
├── src/
│   ├── extractor.py
│   ├── heuristics.py
│   ├── gemini_analyzer.py
│   └── schemas.py
└── tests/
    └── test_heuristics.py
```

## Setup

```bash
git clone <your-repository-url>
cd ai-resume-analyzer
python -m venv .venv
```

Activate the virtual environment:

```bash
# macOS/Linux
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create your local environment file:

```bash
cp .env.example .env
```

Set:

```text
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-3.8-flash
```

Run:

```bash
streamlit run app.py
```

## Run tests

```bash
pytest -q
```

## Design choices

### Why deterministic scoring + an LLM?
A pure LLM "ATS score" is hard to reproduce and audit. This project keeps the numerical score deterministic and uses Gemini for the qualitative layer: strengths, gaps, rewrites, and interview focus areas.

### Why structured Gemini output?
The Google GenAI SDK supports schema-constrained JSON output. This makes the app safer and easier to render than parsing loosely formatted prose.

### Security
- Never commit a real Gemini API key.
- `.env` is ignored by Git.
- The API key is read only from the server process environment.
- Resume text is sent to Gemini only when the AI review is requested.

## Possible next upgrades

- OCR for scanned PDFs
- DOCX ingestion
- semantic skill normalization (e.g. `K8s` → `Kubernetes`)
- embedding-based JD/resume similarity
- section-level scoring
- downloadable PDF analysis report
- Dockerfile + GitHub Actions CI
- evaluation dataset for score calibration
- optional PII redaction before LLM calls

## Inspiration / attribution

Concept inspired by the Medium article **“Build Your Own AI Resume Analyzer with Python and Google Gemini”** by Jyoti Dabass, Ph.D. This repository is an independent implementation with additional JD matching, deterministic scoring, structured output, testing, and security notes.

## License

MIT
