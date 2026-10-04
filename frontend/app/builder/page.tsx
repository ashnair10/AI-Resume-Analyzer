"use client";

import Link from "next/link";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import type { AIReview, Analysis } from "@/lib/types";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const MASTER_KEY = "techcv-master-v1";
const HISTORY_KEY = "techcv-applications-v1";
const field = "w-full rounded-xl border border-white/15 bg-black/25 p-3 text-sm text-zinc-100 outline-none focus:border-violet-400";
const example = `Your Name
AI Engineer | email@example.com | City | github.com/yourname

Summary
Write a short summary grounded in your experience.

Technical Skills
List only technologies you can explain and support.

Experience
Job title | Employer | Start date - End date
- Describe what you built, how you built it, and the verified result.

Projects
Project name | Repository URL
- Describe your contribution and the technologies you actually used.

Education
Degree | Institution | Year`;
type Snapshot = { id: string; savedAt: string; company: string; role: string; content: string; jd: string; template: "classic" | "compact"; highlights: string };
type Review = { analysis: Analysis; ai_review: AIReview | null; ai_error: string | null; ai_enabled: boolean };

async function check(response: Response) {
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(typeof body.detail === "string" ? body.detail : "Request failed. Check your input and API connection.");
  }
  return response;
}
function download(blob: Blob, name: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a"); a.href = url; a.download = name; a.click();
  window.setTimeout(() => URL.revokeObjectURL(url), 1000);
}

export default function BuilderPage() {
  const [content, setContent] = useState("");
  const [company, setCompany] = useState("");
  const [role, setRole] = useState("");
  const [jd, setJd] = useState("");
  const [template, setTemplate] = useState<"classic" | "compact">("compact");
  const [highlights, setHighlights] = useState("Python, FastAPI, RAG");
  const [reviewed, setReviewed] = useState(false);
  const [useAI, setUseAI] = useState(false);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [review, setReview] = useState<Review | null>(null);
  const [reviewSource, setReviewSource] = useState("");
  const [history, setHistory] = useState<Snapshot[]>([]);
  const [confirmations, setConfirmations] = useState<Record<number, boolean>>({});
  const [undo, setUndo] = useState<string[]>([]);
  const freshReview = reviewSource === JSON.stringify([content, jd]);

  function edit(value: string) { setContent(value); setReviewed(false); }
  async function run(action: () => Promise<void>) {
    setBusy(true); setError(""); setMessage("");
    try { await action(); } catch (e) { setError(e instanceof Error ? e.message : "Operation failed"); }
    finally { setBusy(false); }
  }
  function browserAction(action: () => void) {
    setError(""); setMessage("");
    try { action(); } catch { setError("Browser storage is unavailable or full. Download a backup instead."); }
  }
  async function importFile(file?: File) {
    if (!file) return;
    if (file.size > 8 * 1024 * 1024) { setError("Upload a file under 8 MB."); return; }
    await run(async () => {
      const form = new FormData(); form.append("resume", file);
      const response = await check(await fetch(`${API}/api/resume/import`, { method: "POST", body: form }));
      const data = await response.json(); edit(data.content); setMessage(data.note);
    });
  }
  async function analyze() {
    await run(async () => {
      const response = await check(await fetch(`${API}/api/resume/review`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content, job_description: jd, use_ai: useAI }),
      }));
      const data: Review = await response.json(); setReview(data); setReviewSource(JSON.stringify([content, jd])); setConfirmations({});
      if (useAI && !data.ai_review) setMessage(data.ai_error ? `AI review unavailable: ${data.ai_error}. The local checks are available.` : "AI is not configured; the local checks are available.");
    });
  }
  function applyRewrite(index: number) {
    const item = review?.ai_review?.rewrite_suggestions[index];
    if (!item || !freshReview || (item.requires_confirmation && !confirmations[index])) return;
    // Only an exact, unique source match can be replaced. No fuzzy or whole-document edits.
    if (!item.original || content.split(item.original).length !== 2) { setError("Original wording is not a unique exact match. Edit this suggestion manually."); return; }
    setUndo(v => [...v, content]); edit(content.replace(item.original, item.suggested));
    setMessage("Rewrite applied. Review again for suggestions based on the updated resume.");
  }
  function snapshot(): Snapshot { return { id: crypto.randomUUID(), savedAt: new Date().toISOString(), company, role, content, jd, template, highlights }; }
  async function exportFile(format: "bundle" | "docx") {
    await run(async () => {
      const response = await check(await fetch(`${API}/api/resume/export?format=${format}`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content, company, role, job_description: jd, template, highlight_terms: highlights.split(","), reviewed }),
      }));
      const fallback = `${company}_${role}`.replace(/[^a-zA-Z0-9_-]/g, "_") || "Resume";
      const name = response.headers.get("Content-Disposition")?.match(/filename="([^"]+)"/)?.[1] || `${fallback}.${format === "bundle" ? "zip" : "docx"}`;
      download(await response.blob(), name);
      setMessage(format === "bundle" ? "Downloaded DOCX + PDF. Open checks.json for page count and text comparison, and inspect the PDF before applying." : "DOCX downloaded. The bundle includes the matching PDF when LibreOffice is available.");
    });
  }

  return <main className="mx-auto max-w-7xl p-5 text-zinc-100 md:p-8">
    <header className="mb-7 flex flex-wrap items-center justify-between gap-4">
      <div><p className="text-sm text-violet-300">TechCV · Application workspace</p><h1 className="mt-2 text-3xl font-semibold">Your experience. A resume for each role.</h1><p className="mt-2 max-w-3xl text-sm leading-6 text-zinc-400">Start with your master resume, review it against a job description, edit the evidence, and download matching Word and PDF files.</p></div>
      <Link href="/analyze" className="text-sm text-violet-300 underline">Resume analyzer</Link>
    </header>
    {error && <p role="alert" className="mb-4 rounded-xl border border-rose-400/30 p-3 text-rose-300">{error}</p>}
    {message && <p role="status" className="mb-4 rounded-xl border border-violet-400/30 p-3 text-sm text-violet-200">{message}</p>}
    <div className="grid gap-5 lg:grid-cols-[1.2fr_1fr]">
      <div className="space-y-5">
        <Card><CardHeader><h2 className="font-semibold">1. Master resume and application draft</h2></CardHeader><CardContent className="space-y-4">
          <div className="flex flex-wrap items-center gap-2">
            <label className="cursor-pointer rounded-xl border border-white/15 p-2 text-sm">Import DOCX / PDF<input aria-label="Import resume" disabled={busy} type="file" accept=".pdf,.docx" className="mt-2 block max-w-60 text-xs" onChange={e => { void importFile(e.target.files?.[0]); e.target.value = ""; }} /></label>
            <Button variant="secondary" onClick={() => browserAction(() => { localStorage.setItem(MASTER_KEY, content); setMessage("Master resume saved in this browser. Download a text backup to keep a separate copy."); })} disabled={busy || !content}>Save master</Button>
            <Button variant="secondary" onClick={() => browserAction(() => { const saved = localStorage.getItem(MASTER_KEY); if (!saved) { setError("No master saved in this browser."); return; } edit(saved); setMessage("Master loaded as a new draft. Set the target job below."); })} disabled={busy}>Load master</Button>
            <Button variant="ghost" onClick={() => edit(example)} disabled={busy || !!content}>Use blank template</Button>
          </div>
          <p className="text-xs leading-5 text-zinc-400">The first line is your name. Use section headings such as Summary, Experience, Technical Skills, Projects, Education, or prefix a custom heading with ##. Begin bullets with a hyphen. Imports preserve text, not the original design.</p>
          <label className="block text-sm">Resume text<textarea aria-label="Resume text" value={content} onChange={e => edit(e.target.value)} className={`${field} mt-2 h-[480px] font-mono leading-6`} placeholder={example} maxLength={40000} /></label>
          <div className="flex flex-wrap gap-2">
            <Button variant="secondary" disabled={!content} onClick={() => download(new Blob([content], { type: "text/plain;charset=utf-8" }), "master-resume.txt")}>Download text backup</Button>
            <Button variant="ghost" disabled={!undo.length} onClick={() => { edit(undo[undo.length - 1]); setUndo(v => v.slice(0, -1)); }}>Undo rewrite</Button>
          </div>
          <p className="text-xs leading-5 text-zinc-400">Save master and Save application store personal text in this browser only. Export files yourself for a durable copy. Clearing browser data removes saved drafts.</p>
        </CardContent></Card>
        <Card><CardHeader><h2 className="font-semibold">2. Target job</h2></CardHeader><CardContent className="space-y-4">
          <div className="grid gap-3 sm:grid-cols-2"><label className="text-sm">Company<input value={company} maxLength={120} onChange={e => setCompany(e.target.value)} className={`${field} mt-2`} /></label><label className="text-sm">Role<input value={role} maxLength={120} onChange={e => setRole(e.target.value)} className={`${field} mt-2`} /></label></div>
          <label className="block text-sm">Job description<textarea value={jd} onChange={e => { setJd(e.target.value); setReviewed(false); }} className={`${field} mt-2 h-44 leading-6`} maxLength={20000} placeholder="Paste the full job description" /></label>
          <label className="flex gap-2 text-sm"><input type="checkbox" checked={useAI} onChange={e => setUseAI(e.target.checked)} />AI rewrite suggestions (sends resume and JD to the configured Gemini provider)</label>
          <Button onClick={() => void analyze()} disabled={busy || content.trim().length < 40 || jd.trim().length < 80}>{busy ? "Working…" : "Review for this job"}</Button>
          <p className="text-xs leading-5 text-zinc-400">Local checks run without AI. Missing keywords are prompts to inspect your experience; add a skill only when you have real evidence for it.</p>
        </CardContent></Card>
      </div>
      <div className="space-y-5">
        <Card><CardHeader><h2 className="font-semibold">3. Review and tailor</h2></CardHeader><CardContent className="space-y-4">
          {!review && <p className="text-sm leading-6 text-zinc-400">Run a review to see gaps and optional rewrite suggestions. Improve bullets with the problem, your contribution, technologies used, and a verified result. Include stakeholder discovery and personal projects where relevant.</p>}
          {review && <>
            {!freshReview && <p className="text-sm text-amber-300">Draft or JD changed. Run review again to refresh these findings.</p>}
            <p className="text-sm">Role Evidence Score: <strong>{review.analysis.role_evidence_score}/100</strong></p>
            <p className="text-xs leading-5 text-zinc-400">This project&apos;s heuristic score is not an ATS score, Naukri percentile, or probability of selection.</p>
            <p className="text-sm text-zinc-300">Keywords to investigate: {review.analysis.missing_keywords.join(", ") || "None identified"}</p>
            {review.ai_review && <><p className="text-sm leading-6 text-violet-200">{review.ai_review.role_summary}</p><ul className="list-disc space-y-2 pl-5 text-sm text-zinc-300">{review.ai_review.material_gaps.map((gap, i) => <li key={i}>{gap}</li>)}</ul></>}
            {review.ai_review?.rewrite_suggestions.map((item, index) => <div key={index} className="space-y-3 rounded-xl border border-white/10 p-3 text-sm">
              <p className="text-zinc-400">Original: {item.original}</p><p className="text-emerald-200">Suggested: {item.suggested}</p><p className="text-xs text-zinc-400">{item.reason}</p>
              {item.requires_confirmation && <label className="flex items-start gap-2 text-amber-200"><input type="checkbox" checked={!!confirmations[index]} onChange={e => setConfirmations(v => ({ ...v, [index]: e.target.checked }))} />I can verify the added facts or scope.</label>}
              <Button variant="secondary" disabled={!freshReview || (item.requires_confirmation && !confirmations[index])} onClick={() => applyRewrite(index)}>Apply this rewrite</Button>
            </div>)}
          </>}
        </CardContent></Card>
        <Card><CardHeader><h2 className="font-semibold">4. Download application files</h2></CardHeader><CardContent className="space-y-4">
          <label className="block text-sm">Template<select value={template} onChange={e => setTemplate(e.target.value as "classic" | "compact")} className={`${field} mt-2`}><option value="compact">Compact · tighter spacing · single column</option><option value="classic">Classic · more breathing room · single column</option></select></label>
          <label className="block text-sm">Bold these terms (comma separated)<input value={highlights} onChange={e => setHighlights(e.target.value)} className={`${field} mt-2`} placeholder="Python, Camunda, RAG, 88%" /></label>
          <p className="text-xs leading-5 text-zinc-400">Bold applies only to existing words; it does not add skills. Both formats use the same DOCX layout. The PDF bundle includes page count, extracted text from both files, and a comparison check.</p>
          <label className="flex items-start gap-2 text-sm"><input type="checkbox" checked={reviewed} onChange={e => setReviewed(e.target.checked)} />I reviewed the draft and can support its claims, dates, metrics, and technologies.</label>
          <div className="flex flex-wrap gap-2"><Button disabled={busy || !reviewed || !company.trim() || !role.trim() || content.trim().length < 40} onClick={() => void exportFile("bundle")}>Download DOCX + PDF</Button><Button variant="secondary" disabled={busy || !reviewed || content.trim().length < 40} onClick={() => void exportFile("docx")}>DOCX only</Button></div>
          <p className="text-xs leading-5 text-zinc-400">Open the exported PDF to check layout before uploading. Fonts and pagination in Microsoft Word may vary. Neither template reproduces an uploaded design exactly.</p>
          <Button variant="secondary" disabled={!content} onClick={() => browserAction(() => { const old: Snapshot[] = JSON.parse(localStorage.getItem(HISTORY_KEY) || "[]"); const updated = [snapshot(), ...old].slice(0, 20); localStorage.setItem(HISTORY_KEY, JSON.stringify(updated)); setHistory(updated); setMessage("Application saved in this browser."); })}>Save application version</Button>
          <Button variant="ghost" onClick={() => browserAction(() => setHistory(JSON.parse(localStorage.getItem(HISTORY_KEY) || "[]")))}>Show saved applications</Button>
          {history.map(item => <button key={item.id} className="block w-full rounded-xl border border-white/10 p-3 text-left text-sm" onClick={() => { edit(item.content); setCompany(item.company); setRole(item.role); setJd(item.jd); setTemplate(item.template); setHighlights(item.highlights); setReview(null); setUndo([]); setMessage("Saved application loaded. Review before re-exporting."); }}>{item.company || "Application"} · {item.role || "Resume"}<span className="mt-1 block text-xs text-zinc-400">{new Date(item.savedAt).toLocaleString()}</span></button>)}
          <Button variant="ghost" onClick={() => browserAction(() => { localStorage.removeItem(MASTER_KEY); localStorage.removeItem(HISTORY_KEY); setHistory([]); setMessage("Saved browser data cleared. The current draft remains open."); })}>Clear saved browser data</Button>
        </CardContent></Card>
      </div>
    </div>
  </main>;
}
