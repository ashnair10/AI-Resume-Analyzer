# TechCV

**Evidence-first AI resume builder for developers and tech professionals.**

TechCV maps a target job description to evidence in a candidate's real experience before recommending resume changes. It separates **keyword coverage** from **evidence strength**, flags claims that need confirmation, and provides an explainable **Role Evidence Score** instead of pretending to reproduce a proprietary ATS score.

## What is included in this build

- Next.js + React + TypeScript frontend
- shadcn/ui-style source components built on Radix primitives
- Tailwind CSS v4
- Motion for React (Framer Motion successor)
- FastAPI + Pydantic backend
- PDF and DOCX resume parsing
- Explainable requirement/evidence analysis
- ClaimCheck / truth-aware review when Gemini is enabled
- Recruiter 10-second scan and rewrite diffs when Gemini is enabled
- Structured JSON application logs
- End-to-end `trace_id` propagation from UI -> API -> analysis
- OpenTelemetry-ready FastAPI instrumentation
- Lightweight input guardrails for PII/injection signals
- Isolated AI Gateway boundary for future Azure OpenAI / Foundry routing
- Optional integration points for Langfuse, Azure Monitor/Application Insights, Azure Content Safety

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
5. Inspect Role Evidence Score, Evidence Map, ClaimCheck, AI review and Trace tabs.

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

### v0.5 — Resume Builder
- master developer profile
- project/achievement evidence vault
- accepted/rejected rewrite state
- ATS-safe DOCX/PDF generation
- smart emphasis/bolding

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
