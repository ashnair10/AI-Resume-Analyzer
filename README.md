# TechCV — Gemini + Transparent ATS Heuristics (AI Resume Coach)

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
techcv/
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

## Built with

### Technologies

- **Python** is used for the application and analysis logic.
- **Streamlit** provides the interactive web interface, including PDF upload, job-description input, scorecards, and review results.
- **PyMuPDF** extracts text, page counts, font families, and font sizes from uploaded PDFs.
- **Google Gen AI SDK** sends the resume, job description, and heuristic results to the configured Gemini model for qualitative feedback.
- **Pydantic** defines and validates the structured Gemini review.
- **python-dotenv** loads local environment variables from `.env`; deployment environments can provide the same variables directly.
- **pytest** runs the automated tests.
- Python standard-library modules, including `re`, `collections.Counter`, and `dataclasses`, support tokenization, frequency counting, and typed document data.

### How the application works

1. Streamlit accepts a PDF resume and a job description.
2. PyMuPDF extracts resume text and document metadata.
3. Local, deterministic heuristics compare job-description keywords with resume tokens and check for resume sections, impact evidence, and basic formatting signals.
4. The app displays the heuristic scores and matching or missing keywords.
5. When analysis is requested, the Gemini API generates qualitative feedback constrained to the `ResumeAIReview` schema.

### Efficiency and reliability choices

- Resume tokens are stored in a **set**, making keyword membership checks efficient.
- **`Counter`** aggregates job-description keyword and PDF font frequencies; only the most frequent keywords and fonts are retained for analysis or display.
- The Gemini prompt is bounded to **12,000 characters of job description** and **18,000 characters of resume text**, helping limit request size, latency, and API usage.
- The Gemini call runs as part of the user's Analyze action rather than on every page render.
- Numeric scoring is performed locally with deterministic rules, keeping it repeatable and independent of the LLM response.
- Gemini's response is requested as JSON conforming to a Pydantic model, instead of relying on unstructured prose parsing.

These are practical design and efficiency choices, not the result of formal performance benchmarking. The project does not currently implement caching, OCR, or semantic keyword matching.

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

## Advanced features & roadmap

Below are recommended enhancements to make TechCV more useful and production-ready. They are prioritized roughly from high-impact to lower-effort:

1. OCR (Tesseract or Google Vision) for scanned or image-only PDFs, with confidence-aware fallbacks.
2. DOCX and plain-text ingestion to cover more resume formats and preserve semantic structure (headings, lists).
3. Semantic skill normalization and aliasing (e.g., `K8s` → `Kubernetes`, `PyTorch` → `PyTorch`) using a small curated dictionary plus fuzzy matching.
4. Embedding-based JD/resume similarity (sentence-BERT or small OpenAI/Gemini embeddings) to surface semantically related skills and role fit beyond token overlap.
5. Section-level scoring: score each resume section (Summary, Experience, Skills, Education, Projects) separately and show per-section suggestions.
6. Guided rewrite templates: generate tailored bullet rewordings that preserve truth (use schema to ensure the LLM does not invent metrics).
7. Downloadable PDF or DOCX report generation for sharing with recruiters.
8. User accounts and a resume history dashboard to compare versions and show progress over time (requires auth and privacy considerations).
9. A/B testing harness for prompt and heuristic experiments to iterate on what reviewers and recruiters prefer.
10. CI, linting, and unit/integration tests for extraction edge cases, prompt behavior, and quality metrics.

## Resume improvement suggestions and common mistakes

These recommendations can be surfaced to users directly from TechCV's UI as actionable tips:

- Prefer measurable impact: include specific numbers (%, absolute improvements, time saved) and context for achievements.
- Use action-first bullet points: start bullets with strong verbs ("Improved", "Reduced", "Designed").
- Tailor to the JD: emphasize top JD keywords in the Summary and top experience bullets, but avoid keyword stuffing.
- Keep formatting ATS-friendly: avoid complex tables and unusual fonts; use standard section headers.
- Keep most resumes to 1–2 pages unless seniority requires more detail.
- Make skills and tools easy to find: a dedicated "Skills" section helps both ATS and human reviewers.
- Avoid vague phrases: replace "Responsible for" with specific outcomes.

## UX feature ideas to nudge better resumes

- Highlight exact lines where a missing keyword would best fit and offer inline rewrite suggestions.
- Provide example reformulated bullets (short, quantified, context→action→impact structure).
- Offer a "resume checklist" (sections present, number of quantified bullets, common formatting flags).
- Show an "expected seniority" estimate from resume length, titles, and experience to guide length/level recommendations.
- Let users mark which bullets are supported (truth check) before generating new suggested metrics.



## Inspiration / attribution

Concept inspired by the Medium article **“Build Your Own AI Resume Analyzer with Python and Google Gemini”** by Jyoti Dabass, Ph.D. This repository is an independent implementation with additional JD matching, deterministic scoring, structured output, testing, and security notes.

## License

MIT
