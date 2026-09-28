import { useState } from "react";
import { getFeedback, exportResume } from "../api.js";

export default function FeedbackPanel({ resumeId, jdId }) {
  const [status, setStatus] = useState("idle"); // idle | loading | done | error
  const [feedback, setFeedback] = useState(null);
  const [errorMessage, setErrorMessage] = useState("");
  const [exportError, setExportError] = useState("");

  async function handleGenerate() {
    setStatus("loading");
    setErrorMessage("");
    try {
      const res = await getFeedback(resumeId, jdId);
      setFeedback(res.feedback);
      setStatus("done");
    } catch (err) {
      setErrorMessage(err.message || "Something went wrong.");
      setStatus("error");
    }
  }

  // Works with or without AI suggestions: without them the PDF is just the
  // clean, ATS-friendly rebuild; with them, approved rewrites are applied.
  const rewrites = feedback?.bullet_rewrites ?? [];

  async function handleDownload() {
    setExportError("");
    try {
      await exportResume(resumeId, rewrites);
    } catch (err) {
      setExportError(err.message || "Could not generate the PDF.");
    }
  }

  return (
    <div className="border-t border-line pt-5 mt-2">
      <div className="flex items-center justify-between mb-3">
        <p className="font-serif text-lg">Suggestions</p>
        {status !== "loading" && (
          <button
            onClick={handleGenerate}
            className="text-sm border border-ink px-3 py-1.5 rounded-sm hover:bg-ink hover:text-paper transition-colors"
          >
            {status === "done" ? "Regenerate" : "Get AI suggestions"}
          </button>
        )}
      </div>

      {status === "idle" && (
        <p className="text-sm text-ink-soft">
          Generate specific rewrite suggestions for your bullet points, grounded
          only in what's actually in your resume — nothing invented.
        </p>
      )}

      {status === "loading" && (
        <p className="text-sm text-ink-soft">Analyzing your resume against the job description…</p>
      )}

      {status === "error" && <p className="text-sm text-rust">{errorMessage}</p>}

      {status === "done" && feedback && (
        <div className="space-y-5">
          {feedback.bullet_rewrites.length > 0 && (
            <div>
              <p className="text-sm font-medium text-ink mb-2">Bullet point rewrites</p>
              <div className="space-y-3">
                {feedback.bullet_rewrites.map((item, i) => (
                  <div key={i} className="text-sm">
                    <p className="text-ink-soft line-through decoration-line">{item.original}</p>
                    <p className="text-ink mt-0.5">{item.improved}</p>
                    {item.reason && <p className="text-xs text-teal mt-0.5">{item.reason}</p>}
                  </div>
                ))}
              </div>
            </div>
          )}

          {feedback.missing_skill_notes.length > 0 && (
            <div>
              <p className="text-sm font-medium text-ink mb-2">On missing skills</p>
              <ul className="space-y-1">
                {feedback.missing_skill_notes.map((item, i) => (
                  <li key={i} className="text-sm text-ink-soft">
                    <span className="text-amber font-medium">{item.skill}:</span> {item.suggestion}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {feedback.tone_notes.length > 0 && (
            <div>
              <p className="text-sm font-medium text-ink mb-2">General notes</p>
              <ul className="space-y-1">
                {feedback.tone_notes.map((note, i) => (
                  <li key={i} className="text-sm text-ink-soft">{note}</li>
                ))}
              </ul>
            </div>
          )}

          {feedback.bullet_rewrites.length === 0 &&
            feedback.missing_skill_notes.length === 0 &&
            feedback.tone_notes.length === 0 && (
              <p className="text-sm text-ink-soft">
                No specific suggestions — your resume already covers the detected requirements well.
              </p>
            )}
        </div>
      )}

      <div className="pt-5">
        <button
          onClick={handleDownload}
          className="text-sm border border-teal text-teal px-3 py-1.5 rounded-sm hover:bg-teal hover:text-paper transition-colors"
        >
          {rewrites.length > 0 ? "Download improved resume (PDF)" : "Download clean ATS-friendly PDF"}
        </button>
        <p className="text-xs text-ink-soft mt-2">
          A simplified single-column rebuild of your resume — a preview of how an ATS reads it, not a replacement for your original file.
        </p>
        {exportError && <p className="text-sm text-rust mt-2">{exportError}</p>}
      </div>
    </div>
  );
}
