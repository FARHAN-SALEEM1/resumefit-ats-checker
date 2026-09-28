const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function handleResponse(res) {
  if (!res.ok) {
    let detail = `Request failed (${res.status})`;
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch {
      // response wasn't JSON — keep the generic message
    }
    throw new Error(detail);
  }
  return res.json();
}

export async function uploadResume(file, userId = 1) {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("user_id", userId);

  const res = await fetch(`${API_BASE}/resumes/upload`, {
    method: "POST",
    body: formData,
  });
  return handleResponse(res);
}

export async function submitJobDescription(rawText, userId = 1) {
  const res = await fetch(`${API_BASE}/job-descriptions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ raw_text: rawText, user_id: userId }),
  });
  return handleResponse(res);
}

export async function analyze(resumeId, jdId) {
  const res = await fetch(`${API_BASE}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ resume_id: resumeId, jd_id: jdId }),
  });
  return handleResponse(res);
}

export async function getFeedback(resumeId, jdId) {
  const res = await fetch(`${API_BASE}/feedback`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ resume_id: resumeId, jd_id: jdId }),
  });
  return handleResponse(res);
}

export async function exportResume(resumeId, bulletRewrites) {
  const res = await fetch(`${API_BASE}/export-resume`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ resume_id: resumeId, bullet_rewrites: bulletRewrites }),
  });
  if (!res.ok) {
    let detail = `Export failed (${res.status})`;
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch {
      // ignore
    }
    throw new Error(detail);
  }
  const blob = await res.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `resume_improved_${resumeId}.pdf`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(url);
}

export async function listAnalyses(userId = 1) {
  const res = await fetch(`${API_BASE}/analyses?user_id=${userId}`);
  return handleResponse(res);
}

export async function getAnalysis(analysisId) {
  const res = await fetch(`${API_BASE}/analyses/${analysisId}`);
  return handleResponse(res);
}
