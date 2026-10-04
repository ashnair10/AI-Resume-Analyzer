import type { AnalyzeResponse } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function analyzeResume(file: File, jobDescription: string, useAI: boolean) {
  const form = new FormData();
  form.append("resume", file);
  form.append("job_description", jobDescription);
  form.append("use_ai", String(useAI));

  const traceId = crypto.randomUUID().replaceAll("-", "");
  const response = await fetch(`${API_URL}/api/analyze`, {
    method: "POST",
    headers: { "x-trace-id": traceId },
    body: form,
  });

  if (!response.ok) {
    let message = "Analysis failed";
    try {
      const body = await response.json();
      message = body.detail || message;
    } catch {}
    throw new Error(message);
  }

  return (await response.json()) as AnalyzeResponse;
}
