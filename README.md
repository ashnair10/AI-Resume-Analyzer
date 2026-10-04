# TechCV

**Evidence-first AI resume builder for developers and tech professionals.**

TechCV maps a target job description to evidence in a candidate's real experience before recommending resume changes. It separates **keyword coverage** from **evidence strength**, flags claims that need confirmation, and provides an explainable **Role Evidence Score** instead of pretending to reproduce a proprietary ATS score.

[View the rendered project guide](https://ashnair10.github.io/AI-Resume-Analyzer/) in your browser, or [view the HTML source](./TECHCV_PROJECT_DOCUMENTATION.html).

## What is included in this build

- Next.js + React + TypeScript frontend
- shadcn/ui-style source components built on Radix primitives
- Tailwind CSS v4
- Motion for React (Framer Motion successor)
- FastAPI + Pydantic backend
- PDF and DOCX resume parsing
- Explainable requirement/evidence analysis
- Actionable deterministic feedback for resume sections, passive/long bullets, common spelling and capitalization checks, word count, and layout review
- ClaimCheck / truth-aware review when Gemini is enabled
- Recruiter 10-second scan and rewrite diffs when Gemini is enabled
- Structured JSON application logs
- End-to-end `trace_id` propagation from UI -> API -> analysis
- OpenTelemetry-ready FastAPI instrumentation
- Lightweight input guardrails for PII/injection signals
- Isolated AI Gateway boundary for future Azure OpenAI / Foundry routing
- Optional integration points for Langfuse, Azure Monitor/Application Insights, Azure Content Safety

## Resume builder for each application

Open **Resume Builder** from the analyzer, or visit `http://localhost:3000/builder`.

1. Import your master DOCX/PDF or use the blank template. Check imported reading order and headings; original visual designs are not preserved.
2. Save the master in your browser and download a text backup. Load it for each new application rather than overwriting it with a tailored version.
3. Enter the company, role, and full JD. Run local evidence checks, or opt into Gemini review for semantic gaps and proposed rewrites.
4. Edit your draft. Apply individual AI rewrites only when the original is a unique exact match; confirm added facts when flagged. Undo is available. Editing the resume or JD marks the review stale.
5. Choose **Classic**, **Modern Blue**, or **Compact** single-column templates. Add comma-separated terms for selective bolding. Terms only style existing text; they do not insert skills.
6. Confirm the facts and download **DOCX + PDF**. The ZIP includes both files, the source draft, JD, extracted text from each format, and `checks.json` with PDF page count and extraction parity.
7. Inspect the PDF and checks before uploading. Save the application version in your browser if desired; the last 20 saved applications can be reloaded.

PDFs are converted from the generated DOCX through LibreOffice, avoiding separate layouts and divergent content. A per-request temporary directory and LibreOffice profile isolate concurrent conversions; temporary files are deleted after each request. No resume database is added. Export responses disable HTTP caching.

### PDF converter setup

Docker builds install LibreOffice Writer and Liberation fonts automatically. For local development:

- Windows: install LibreOffice and add its `program` directory to `PATH`.
- macOS: install LibreOffice and ensure `soffice` is available on `PATH` (the executable is inside the application bundle).
- Ubuntu/Debian: `sudo apt-get install libreoffice-writer fonts-liberation`.

If conversion fails or times out, the UI reports it and **DOCX only** remains available. Never substitute a renamed DOCX as a PDF.

### What these checks mean

Matching extracted text is a useful format check, not a promise of equal ATS results. The builder does not reproduce Naukri percentiles, Google screening rules, employer ATS scoring, or rejection probabilities. The same content can be treated differently by downstream parsers. Verify important contact details, headings, URLs, and technical terms after import and export.

The deterministic analyzer uses lexical matching and conservative action/metric evidence rules, not a complete semantic evaluation. Its improvement list includes limited spelling/capitalization checks and advisory bullet, length, and layout prompts; it is not a full grammar checker and cannot reliably infer visual columns or pagination from extracted text. Skills lists and dates alone do not establish strong project evidence. Gemini suggestions still require human review and can be wrong. The builder does not invent metrics, certifications, tools, or job experience during export.

Browser saves are opt-in, confined to the current browser/device, and lost if site data is cleared. **Clear saved browser data** removes the saved master and application history. Keep a downloaded backup. Export ZIPs contain personal text and the target JD; keep them private. With AI review enabled, the resume and JD are sent to the configured Gemini provider. The local heuristic path and document export do not call a model.

The templates are built-in text-based single-column designs, not exact copies of an uploaded resume. Microsoft Word may paginate differently from LibreOffice. Scanned PDF import needs OCR before use. Job tailoring remains an editable, reviewed workflow; there is no automatic application submission.

## Architecture

```text
Next.js / React
   |  x-trace-id
   v
FastAPI
   |-- document parser (PDF/DOCX)
   |-- deterministic evidence engine
   |-- guardrails
   |-- AI Gateway
   |      `-- Gemini today; Azure OpenAI/Foundry can be added later
   |
   `-- structured telemetry
          |-- JSON logs
          `-- OpenTelemetry (optional)

Deployment adapters (optional):
OpenTelemetry -> Azure Monitor / Application Insights / Collector
AI traces      -> Langfuse
Guardrails     -> Azure AI Content Safety + Presidio
Secrets        -> Azure Key Vault
API edge       -> Azure API Management
```

The local project intentionally does **not** require Azure, Langfuse, n8n, or a cloud account. Those are deployment/platform capabilities, not prerequisites for developing the resume product.

## 1. Run the FastAPI backend

Windows PowerShell:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload --port 8000
```

macOS/Linux:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

Check:

```text
http://localhost:8000/health
http://localhost:8000/docs
```

### Gemini is optional

The deterministic Evidence Map works without any API key. To enable semantic JD decomposition, ClaimCheck, recruiter scan and rewrite suggestions, edit `backend/.env`:

```env
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-2.5-flash
```

Never commit `.env`.

## 2. Run the Next.js frontend

Open another terminal:

```powershell
cd frontend
npm install
Copy-Item .env.local.example .env.local
npm run dev
```

Open:

```text
http://localhost:3000
```

## 3. Test it

1. Upload a PDF or DOCX resume.
2. Paste a job description (a sample developer/AI JD is prefilled).
3. Leave **AI-enhanced review** on if a Gemini key is configured, or switch it off for deterministic-only testing.
4. Select **Analyze**.
5. Start with **Your improvements** for actionable writing and structure suggestions, then inspect **Role gaps**, ClaimCheck, AI review and Trace. Generic job-description wording is filtered from role-gap keywords; direct lexical matches remain heuristic signals, not proof of skill.

Backend tests:

```bash
cd backend
pytest -q
```

Frontend production build:

```bash
cd frontend
npm run build
```

## Observability & governance design

### Trace IDs

The frontend creates a trace ID for each analysis request and sends it as `x-trace-id`. FastAPI reuses it in structured logs and returns it to the UI.

No resume text is intentionally logged.

### OpenTelemetry

Local mode is off by default. To enable OTLP trace export:

```env
OTEL_ENABLED=true
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318/v1/traces
```

This keeps telemetry vendor-neutral. In Azure, configure an OpenTelemetry/Azure Monitor path rather than putting monitoring calls throughout the application.

### AI Gateway

`backend/core/ai_gateway.py` is the only application boundary that should know which model provider is being used. Future capabilities belong here or behind this boundary:

- Azure OpenAI / Azure AI Foundry
- prompt registry/version IDs
- Langfuse generation traces
- token/cost metrics
- model routing/fallback
- Azure AI Content Safety
- output schema validation and policy checks

### Guardrails

This build includes lightweight PII and prompt-injection signal detection for the JD. For production, extend the guardrail layer with:

- Microsoft Presidio for PII detection/redaction
- Azure AI Content Safety
- prompt-injection classifiers/policies
- schema validation
- claim provenance and confirmation state

### n8n

Do **not** add n8n just to analyze a resume. Use it later for cross-system workflows such as application tracking, job ingestion, notifications, or approval flows. Keep the core resume analysis path directly behind FastAPI for simplicity and latency.

## Integrating with your existing `AI-Resume-Analyzer` repository

Recommended end-state:

```text
AI-Resume-Analyzer/
├── frontend/          # this Next.js app
├── backend/           # this FastAPI + existing Python analysis logic
├── docker-compose.yml
├── README.md
└── LICENSE
```

Your previous Streamlit entrypoint can be preserved temporarily under `legacy/streamlit-app/` until the Next.js UI reaches feature parity, then removed.

## Product roadmap

### v0.3 — Evidence Workspace (this build)
- Role Evidence Score
- requirement -> evidence map
- ClaimCheck
- smooth developer-focused UI
- FastAPI split
- traceability and guardrail foundation

### v0.4 — Developer Evidence Graph
- normalize technologies (`k8s` -> `Kubernetes`, `Fast API` -> `FastAPI`)
- embeddings/semantic requirement matching
- project/work evidence provenance
- interactive Truth Guard confirmations

### Resume Builder — implemented in this update
- browser-saved master resume and application versions
- individual accepted rewrites with fact confirmation and undo
- single-source DOCX/PDF bundles with extraction checks
- compact/classic single-column templates and selective bolding

### Next builder improvements
- structured evidence vault and per-claim provenance
- exact custom DOCX template preservation
- side-by-side version comparisons
- authenticated cross-device profile storage

### v0.6 — Experiment Lab
- Resume A/B comparison
- explainable evidence diff
- application/version history
- regression tests for resume changes

### v1.0 — Developer Resume Compiler
- master career evidence -> target job -> verified role-specific resume
- GitHub/project evidence (opt-in)
- interview-defense view for every major claim

## Product principle

> **A missing keyword is not permission to invent a skill.**

TechCV should recommend the strongest truthful wording supported by the candidate's actual work.

AI review accepts at most 20,000 resume characters and 14,000 JD characters. Larger inputs return an explicit limit message rather than a silently truncated AI review. Local checks accept the entire builder draft up to 40,000 characters and JD up to 20,000 characters.
