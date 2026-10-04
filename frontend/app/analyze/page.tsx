"use client";

import { useMemo, useRef, useState } from "react";
import { AnimatePresence, motion } from "motion/react";
import { Activity, ArrowRight, Braces, CheckCircle2, FileText, Gauge, GitCompareArrows, LockKeyhole, ScanSearch, ShieldCheck, Sparkles, Upload, X } from "lucide-react";
import { analyzeResume } from "@/lib/api";
import type { AnalyzeResponse } from "@/lib/types";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScoreRing } from "@/components/analysis/score-ring";
import { EvidenceCard } from "@/components/analysis/evidence-card";

const nav = [
  [ScanSearch, "Analyze", true],
  [FileText, "Resume Builder", false],
  [Braces, "Evidence", false],
  [GitCompareArrows, "Compare", false],
];

const sampleJD = `We are looking for a Senior AI Engineer to build production GenAI applications. You will design Python APIs, retrieval-augmented generation (RAG) pipelines, evaluation workflows and secure document-processing systems. Experience with FastAPI, Azure, Docker/Kubernetes, LLM observability, prompt engineering and human-in-the-loop workflows is important. You should be able to own systems end-to-end, collaborate with stakeholders and improve reliability using monitoring, tracing and structured evaluation.`;

function metricLabel(key: string) {
  return key.replaceAll("_score", "").replaceAll("_", " ");
}

export default function AnalyzePage() {
  const [file, setFile] = useState<File | null>(null);
  const [jd, setJd] = useState(sampleJD);
  const [useAI, setUseAI] = useState(true);
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  const status = useMemo(() => {
    if (!result) return null;
    const r = result.analysis.readiness;
    if (r === "ready_to_apply") return ["Ready to apply", "text-emerald-300 bg-emerald-400/[.07] border-emerald-400/20"];
    if (r === "improve_before_applying") return ["Improve before applying", "text-amber-300 bg-amber-400/[.07] border-amber-400/20"];
    return ["Weak fit", "text-rose-300 bg-rose-400/[.07] border-rose-400/20"];
  }, [result]);

  async function runAnalysis() {
    if (!file) { setError("Upload a PDF or DOCX resume first."); return; }
    setLoading(true); setError("");
    try { setResult(await analyzeResume(file, jd, useAI)); }
    catch (e) { setError(e instanceof Error ? e.message : "Analysis failed"); }
    finally { setLoading(false); }
  }

  return (
    <main className="relative min-h-screen overflow-hidden text-zinc-100">
      <div className="grid-noise pointer-events-none absolute inset-0 opacity-60" />
      <div className="pointer-events-none absolute left-1/2 top-0 h-96 w-[48rem] -translate-x-1/2 rounded-full bg-violet-500/10 blur-3xl" />

      <div className="relative mx-auto flex min-h-screen max-w-[1680px]">
        <aside className="hidden w-64 shrink-0 border-r border-white/[.06] p-5 lg:block">
          <div className="mb-9 flex items-center gap-3 px-2">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl border border-violet-400/20 bg-violet-400/10"><Sparkles className="h-4 w-4 text-violet-300" /></div>
            <div><div className="font-semibold tracking-tight">TechCV</div><div className="text-[11px] text-zinc-600">Developer Resume Intelligence</div></div>
          </div>
          <nav className="space-y-1">
            {nav.map(([Icon, label, active]) => {
              const I = Icon as typeof ScanSearch;
              return <button key={label as string} disabled={!active} className={`flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm transition ${active ? "bg-white/[.06] text-white" : "text-zinc-600"}`}><I className="h-4 w-4" />{label as string}{!active && <span className="ml-auto text-[9px] uppercase tracking-wider">soon</span>}</button>;
            })}
          </nav>
          <div className="absolute bottom-6 w-[216px] rounded-2xl border border-white/[.07] bg-white/[.025] p-4">
            <div className="flex items-center gap-2 text-xs font-medium"><ShieldCheck className="h-4 w-4 text-emerald-300" /> Evidence-first</div>
            <p className="mt-2 text-xs leading-5 text-zinc-600">TechCV separates keyword presence from evidence and never treats an unsupported skill as proof.</p>
          </div>
        </aside>

        <section className="min-w-0 flex-1 p-4 md:p-7">
          <header className="mb-6 flex flex-col justify-between gap-4 md:flex-row md:items-end">
            <div>
              <div className="mb-2 flex items-center gap-2"><Badge>Analysis Workspace</Badge><Badge className="border-violet-400/20 bg-violet-400/[.06] text-violet-300">v0.3</Badge></div>
              <h1 className="text-3xl font-semibold tracking-[-.035em] md:text-4xl">Build a resume your experience can prove.</h1>
              <p className="mt-2 max-w-2xl text-sm leading-6 text-zinc-500">Map job requirements to real project evidence, inspect weak claims, and strengthen your resume without keyword stuffing or fabricated experience.</p>
            </div>
            {result && <div className="flex items-center gap-2 text-xs text-zinc-600"><Activity className="h-3.5 w-3.5" /> trace {result.trace_id.slice(0, 10)} · {result.duration_ms} ms</div>}
          </header>

          <div className="grid gap-4 xl:grid-cols-[390px_minmax(0,1fr)]">
            <div className="space-y-4">
              <Card>
                <CardHeader><div className="flex items-center justify-between"><div><div className="text-sm font-medium">1. Resume</div><div className="mt-1 text-xs text-zinc-600">PDF or DOCX · max 8 MB</div></div><Upload className="h-4 w-4 text-zinc-600" /></div></CardHeader>
                <CardContent>
                  <input ref={inputRef} className="hidden" type="file" accept=".pdf,.docx" onChange={e => setFile(e.target.files?.[0] || null)} />
                  <motion.button whileHover={{ scale: 1.006 }} whileTap={{ scale: .995 }} onClick={() => inputRef.current?.click()} className="group flex min-h-28 w-full items-center justify-center rounded-xl border border-dashed border-white/10 bg-white/[.02] px-4 transition hover:border-violet-400/30 hover:bg-violet-400/[.025]">
                    {file ? <div className="flex w-full items-center gap-3"><div className="rounded-lg bg-violet-400/10 p-2"><FileText className="h-4 w-4 text-violet-300" /></div><div className="min-w-0 flex-1 text-left"><div className="truncate text-sm text-zinc-200">{file.name}</div><div className="text-xs text-zinc-600">{(file.size / 1024 / 1024).toFixed(2)} MB</div></div><X onClick={e => { e.stopPropagation(); setFile(null); }} className="h-4 w-4 text-zinc-600" /></div> : <div className="text-center"><Upload className="mx-auto mb-2 h-5 w-5 text-zinc-600 transition group-hover:text-violet-300" /><div className="text-sm text-zinc-300">Choose resume</div><div className="mt-1 text-xs text-zinc-600">Your file stays local to this API session</div></div>}
                  </motion.button>
                </CardContent>
              </Card>

              <Card>
                <CardHeader><div className="text-sm font-medium">2. Target job</div><div className="mt-1 text-xs text-zinc-600">Paste the complete job description.</div></CardHeader>
                <CardContent>
                  <textarea value={jd} onChange={e => setJd(e.target.value)} className="soft-scrollbar h-56 w-full resize-none rounded-xl border border-white/[.08] bg-black/25 p-3 text-sm leading-6 text-zinc-300 outline-none transition placeholder:text-zinc-700 focus:border-violet-400/30 focus:ring-2 focus:ring-violet-400/10" />
                  <div className="mt-3 flex items-center justify-between gap-3">
                    <button onClick={() => setUseAI(v => !v)} className="flex items-center gap-2 text-xs text-zinc-500"><span className={`h-4 w-7 rounded-full p-0.5 transition ${useAI ? "bg-violet-500" : "bg-zinc-800"}`}><motion.span layout className={`block h-3 w-3 rounded-full bg-white ${useAI ? "ml-3" : "ml-0"}`} /></span>AI-enhanced review</button>
                    <Button onClick={runAnalysis} disabled={loading || jd.length < 80}>{loading ? <><motion.span animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1, ease: "linear" }} className="h-3.5 w-3.5 rounded-full border-2 border-zinc-400 border-t-transparent" />Analyzing</> : <>Analyze <ArrowRight className="h-4 w-4" /></>}</Button>
                  </div>
                  {error && <p className="mt-3 text-xs text-rose-300">{error}</p>}
                </CardContent>
              </Card>
            </div>

            <AnimatePresence mode="wait">
              {!result ? (
                <motion.div key="empty" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex min-h-[650px] items-center justify-center rounded-2xl border border-white/[.06] bg-white/[.018] p-8">
                  <div className="max-w-lg text-center">
                    <div className="mx-auto mb-5 flex h-14 w-14 items-center justify-center rounded-2xl border border-white/[.08] bg-white/[.03]"><Gauge className="h-6 w-6 text-zinc-500" /></div>
                    <h2 className="text-xl font-medium tracking-tight">Your evidence map starts here</h2>
                    <p className="mt-2 text-sm leading-6 text-zinc-600">Upload a resume and analyze the target role. TechCV will separate keyword coverage, evidence strength, impact quality, ATS parsability, and claim risk.</p>
                  </div>
                </motion.div>
              ) : (
                <motion.div key="result" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: .35 }} className="space-y-4">
                  <div className="grid gap-4 md:grid-cols-[220px_1fr]">
                    <Card className="flex min-h-52 items-center justify-center"><ScoreRing score={result.analysis.role_evidence_score} /></Card>
                    <Card>
                      <CardHeader><div className="flex flex-wrap items-center justify-between gap-2"><div><div className="text-sm font-medium">Role readiness</div><div className="mt-1 text-xs text-zinc-600">Explainable score, not a proprietary ATS prediction.</div></div>{status && <Badge className={status[1]}>{status[0]}</Badge>}</div></CardHeader>
                      <CardContent>
                        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
                          {(["requirement_coverage_score", "evidence_strength_score", "impact_score", "formatting_score"] as const).map((k, i) => (
                            <motion.div key={k} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: .06 * i }} className="rounded-xl border border-white/[.06] bg-white/[.025] p-3">
                              <div className="text-xl font-semibold">{result.analysis[k]}%</div><div className="mt-1 text-[11px] capitalize text-zinc-600">{metricLabel(k)}</div>
                            </motion.div>
                          ))}
                        </div>
                        <div className="mt-4 flex flex-wrap gap-2"><Badge><LockKeyhole className="mr-1 h-3 w-3" /> PII signals: {result.guardrails.pii_detected ? result.guardrails.pii_types.join(", ") : "none in JD"}</Badge><Badge>AI: {result.ai.enabled ? `${result.ai.provider} · ${result.ai.model}` : "local analysis"}</Badge></div>
                      </CardContent>
                    </Card>
                  </div>

                  <Card>
                    <CardContent className="pt-5">
                      <Tabs defaultValue="evidence">
                        <TabsList><TabsTrigger value="evidence">Evidence map</TabsTrigger><TabsTrigger value="claims">ClaimCheck</TabsTrigger><TabsTrigger value="review">AI review</TabsTrigger><TabsTrigger value="observability">Trace</TabsTrigger></TabsList>
                        <TabsContent value="evidence">
                          <div className="grid gap-2 md:grid-cols-2">{result.analysis.evidence_map.slice(0, 16).map((item, i) => <EvidenceCard key={`${item.requirement}-${i}`} item={item} index={i} />)}</div>
                        </TabsContent>
                        <TabsContent value="claims">
                          <div className="space-y-3">
                            {result.ai_review?.claim_checks?.length ? result.ai_review.claim_checks.map((c, i) => (
                              <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * .04 }} key={i} className="rounded-xl border border-white/[.07] bg-white/[.02] p-4">
                                <div className="flex items-start justify-between gap-3"><p className="text-sm leading-6 text-zinc-200">{c.claim}</p><Badge>{c.status.replaceAll("_", " ")}</Badge></div>
                                <p className="mt-2 text-xs leading-5 text-zinc-500">{c.explanation}</p>
                                {c.safer_rewrite && <div className="mt-3 rounded-lg border border-emerald-400/10 bg-emerald-400/[.035] p-3 text-xs leading-5 text-emerald-100/80"><span className="text-emerald-400">Safer:</span> {c.safer_rewrite}</div>}
                              </motion.div>
                            )) : (
                              <div className="space-y-3">
                                <div className="rounded-xl border border-white/[.06] bg-white/[.02] p-4">
                                  <div className="mb-2 text-xs uppercase tracking-wider text-zinc-600">Deterministic Truth Guard</div>
                                  {result.analysis.subjective_claims.length ? (
                                    <>
                                      <p className="mb-2 text-xs text-amber-200/80">Subjective or inflated wording to review</p>
                                      <ul className="space-y-2">{result.analysis.subjective_claims.map((claim, i) => <li key={i} className="text-sm leading-6 text-zinc-300">{claim}</li>)}</ul>
                                    </>
                                  ) : <p className="text-sm text-zinc-500">No obvious subjective claims detected.</p>}
                                  {result.analysis.weakly_supported_mentions.length > 0 && (
                                    <div className="mt-4">
                                      <p className="mb-2 text-xs text-amber-200/80">Terms needing stronger evidence</p>
                                      <div className="flex flex-wrap gap-2">{result.analysis.weakly_supported_mentions.map((term, i) => <Badge key={`${term}-${i}`}>{term}</Badge>)}</div>
                                    </div>
                                  )}
                                </div>
                                <div className="rounded-xl border border-white/[.06] bg-white/[.02] p-4 text-sm text-zinc-500">
                                  {result.ai.error
                                    ? <>AI review failed: <span className="text-rose-300">{result.ai.error}</span></>
                                    : <>Enable AI-enhanced review and configure <code>GEMINI_API_KEY</code> for semantic ClaimCheck.</>}
                                </div>
                              </div>
                            )}
                          </div>
                        </TabsContent>
                        <TabsContent value="review">
                          {result.ai_review ? (
                            <div className="space-y-5">
                              <div className="rounded-xl border border-white/[.06] bg-white/[.02] p-4">
                                <div className="mb-2 flex items-center justify-between gap-3">
                                  <div className="text-xs uppercase tracking-wider text-zinc-600">Role summary</div>
                                  <Badge>{result.ai_review.readiness.replaceAll("_", " ")}</Badge>
                                </div>
                                <p className="text-sm leading-6 text-zinc-300">{result.ai_review.role_summary}</p>
                                <p className="mt-3 text-sm leading-6 text-violet-100/80">{result.ai_review.final_recommendation}</p>
                              </div>
                              <div className="grid gap-4 lg:grid-cols-2">
                                <div className="rounded-xl border border-white/[.06] bg-white/[.02] p-4">
                                  <div className="mb-3 text-xs uppercase tracking-wider text-zinc-600">Recruiter 10-second scan</div>
                                  <ul className="space-y-2">{result.ai_review.recruiter_10_second_scan.map((x, i) => <li key={i} className="flex gap-2 text-sm text-zinc-400"><CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-violet-300" />{x}</li>)}</ul>
                                </div>
                                <div className="rounded-xl border border-white/[.06] bg-white/[.02] p-4">
                                  <div className="mb-3 text-xs uppercase tracking-wider text-zinc-600">Interview focus</div>
                                  <ul className="space-y-2">{result.ai_review.interview_focus.map((x, i) => <li key={i} className="text-sm leading-6 text-zinc-400">{x}</li>)}</ul>
                                </div>
                                <div className="rounded-xl border border-white/[.06] bg-white/[.02] p-4">
                                  <div className="mb-3 text-xs uppercase tracking-wider text-zinc-600">Strengths</div>
                                  <ul className="space-y-2">{result.ai_review.strengths.map((x, i) => <li key={i} className="text-sm leading-6 text-zinc-400">{x}</li>)}</ul>
                                </div>
                                <div className="rounded-xl border border-white/[.06] bg-white/[.02] p-4">
                                  <div className="mb-3 text-xs uppercase tracking-wider text-zinc-600">Material gaps</div>
                                  <ul className="space-y-2">{result.ai_review.material_gaps.map((x, i) => <li key={i} className="text-sm leading-6 text-zinc-400">{x}</li>)}</ul>
                                </div>
                              </div>
                              <div className="rounded-xl border border-white/[.06] bg-white/[.02] p-4">
                                <div className="mb-3 text-xs uppercase tracking-wider text-zinc-600">JD requirements</div>
                                <div className="flex flex-wrap gap-2">{result.ai_review.requirements.map((item, i) => <Badge key={`${item.requirement}-${i}`}>{item.priority.replaceAll("_", " ")} · {item.requirement}</Badge>)}</div>
                              </div>
                              <div>
                                <div className="mb-3 text-xs uppercase tracking-wider text-zinc-600">AI evidence review</div>
                                <div className="grid gap-2 md:grid-cols-2">{result.ai_review.evidence_map.map((item, i) => (
                                  <div key={`${item.requirement}-${i}`} className="rounded-xl border border-white/[.07] bg-white/[.02] p-4">
                                    <div className="flex items-center justify-between gap-2"><p className="text-sm text-zinc-200">{item.requirement}</p><Badge>{item.status}</Badge></div>
                                    <p className="mt-2 text-xs leading-5 text-zinc-500">{item.explanation}</p>
                                    {item.evidence.length > 0 && <ul className="mt-2 space-y-1">{item.evidence.map((line, j) => <li key={j} className="border-l border-violet-400/30 pl-2 text-xs leading-5 text-zinc-400">{line}</li>)}</ul>}
                                    <p className="mt-2 text-xs leading-5 text-violet-200/70">{item.recommendation}</p>
                                  </div>
                                ))}</div>
                              </div>
                              <div>
                                <div className="mb-3 text-xs uppercase tracking-wider text-zinc-600">Rewrite suggestions</div>
                                <div className="grid gap-2 lg:grid-cols-2">{result.ai_review.rewrite_suggestions.map((x, i) => <div key={i} className="rounded-xl border border-white/[.07] bg-black/20 p-4 text-xs"><div className="text-rose-300/70">− {x.original}</div><div className="mt-2 text-emerald-300/80">+ {x.suggested}</div><div className="mt-2 text-zinc-600">{x.reason}{x.requires_confirmation ? " · confirmation required" : ""}</div></div>)}</div>
                              </div>
                            </div>
                          ) : (
                            <div className="rounded-xl border border-white/[.06] bg-white/[.02] p-5 text-sm text-zinc-500">
                              {result.ai.error
                                ? <>AI review failed: <span className="text-rose-300">{result.ai.error}</span></>
                                : <>AI review wasn't returned for this run. Enable AI-enhanced review and configure <code>GEMINI_API_KEY</code> for semantic analysis.</>}
                            </div>
                          )}
                        </TabsContent>
                        <TabsContent value="observability">
                          <div className="grid gap-3 md:grid-cols-3"><div className="rounded-xl border border-white/[.06] bg-white/[.02] p-4"><div className="text-xs text-zinc-600">Trace ID</div><div className="mt-2 break-all font-mono text-xs text-zinc-300">{result.trace_id}</div></div><div className="rounded-xl border border-white/[.06] bg-white/[.02] p-4"><div className="text-xs text-zinc-600">API latency</div><div className="mt-2 text-2xl font-semibold">{result.duration_ms}<span className="ml-1 text-xs font-normal text-zinc-600">ms</span></div></div><div className="rounded-xl border border-white/[.06] bg-white/[.02] p-4"><div className="text-xs text-zinc-600">Guardrails</div><div className="mt-2 text-sm text-zinc-300">{result.guardrails.prompt_injection_signals.length ? `${result.guardrails.prompt_injection_signals.length} prompt-injection signal(s)` : "No JD injection signal detected"}</div></div></div>
                          <p className="mt-4 max-w-3xl text-xs leading-5 text-zinc-600">The same trace ID is sent from Next.js to FastAPI and written into structured logs. Turn on OpenTelemetry in the backend environment to export traces to an OTLP-compatible collector. Langfuse/Azure integrations remain optional deployment adapters rather than local requirements.</p>
                        </TabsContent>
                      </Tabs>
                    </CardContent>
                  </Card>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </section>
      </div>
    </main>
  );
}
