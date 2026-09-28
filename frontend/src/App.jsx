import { useState } from "react";
import ResumeUpload from "./components/ResumeUpload.jsx";
import JobDescriptionInput from "./components/JobDescriptionInput.jsx";
import Report from "./components/Report.jsx";
import HistoryView from "./components/HistoryView.jsx";
import CompareView from "./components/CompareView.jsx";
import { uploadResume, submitJobDescription, analyze } from "./api.js";

function NavTab({ label, active, onClick }) {
  return (
    <button
      onClick={onClick}
      className={`text-sm pb-1 border-b-2 transition-colors ${
        active ? "border-ink text-ink" : "border-transparent text-ink-soft hover:text-ink"
      }`}
    >
      {label}
    </button>
  );
}

export default function App() {
  // "check" = new analysis | "history" = past analyses | "report" = one reopened | "compare"
  const [view, setView] = useState("check");

  // New-check state
  const [file, setFile] = useState(null);
  const [jdText, setJdText] = useState("");
  const [status, setStatus] = useState("input"); // input | working | done | error
  const [errorMessage, setErrorMessage] = useState("");
  const [result, setResult] = useState(null);

  // History state
  const [openedResult, setOpenedResult] = useState(null);
  const [comparePair, setComparePair] = useState(null);

  const canSubmit = file && jdText.trim().length >= 30 && status !== "working";

  async function handleSubmit() {
    setStatus("working");
    setErrorMessage("");
    try {
      const resumeRes = await uploadResume(file);
      const jdRes = await submitJobDescription(jdText);
      const analysisRes = await analyze(resumeRes.id, jdRes.id);
      setResult(analysisRes);
      setStatus("done");
    } catch (err) {
      setErrorMessage(err.message || "Something went wrong — please try again.");
      setStatus("error");
    }
  }

  function handleStartOver() {
    setFile(null);
    setJdText("");
    setResult(null);
    setStatus("input");
    setErrorMessage("");
  }

  const tab = view === "check" ? "check" : "history";

  return (
    <div className="min-h-screen">
      <header className="border-b border-line">
        <div className="max-w-2xl mx-auto px-6 pt-6">
          <h1 className="font-serif text-2xl">ResumeFit</h1>
          <p className="text-sm text-ink-soft mt-1">
            Check your resume against a real job posting before you apply —
            built for the Pakistani job market.
          </p>
          <nav className="flex gap-6 mt-5">
            <NavTab label="New check" active={tab === "check"} onClick={() => setView("check")} />
            <NavTab label="History" active={tab === "history"} onClick={() => setView("history")} />
          </nav>
        </div>
      </header>

      <main className="max-w-2xl mx-auto px-6 py-10">
        {view === "check" && (
          <>
            {status !== "done" && (
              <div className="space-y-6">
                <ResumeUpload file={file} onFileSelected={setFile} />
                <JobDescriptionInput value={jdText} onChange={setJdText} />

                {status === "error" && <p className="text-sm text-rust">{errorMessage}</p>}

                <button
                  onClick={handleSubmit}
                  disabled={!canSubmit}
                  className="bg-ink text-paper text-sm px-5 py-2.5 rounded-sm
                    disabled:opacity-30 disabled:cursor-not-allowed
                    hover:bg-teal transition-colors"
                >
                  {status === "working" ? "Checking…" : "Check my resume"}
                </button>
              </div>
            )}

            {status === "done" && result && (
              <div>
                <p className="text-xs text-ink-soft mb-6">Saved to your History.</p>
                <Report result={result} />
                <button
                  onClick={handleStartOver}
                  className="mt-8 text-sm text-ink-soft underline underline-offset-2 hover:text-ink"
                >
                  Check another resume or job
                </button>
              </div>
            )}
          </>
        )}

        {view === "history" && (
          <HistoryView
            onOpen={(r) => {
              setOpenedResult(r);
              setView("report");
            }}
            onCompare={(a, b) => {
              setComparePair([a, b]);
              setView("compare");
            }}
          />
        )}

        {view === "report" && openedResult && (
          <div>
            <button
              onClick={() => setView("history")}
              className="mb-6 text-sm text-ink-soft underline underline-offset-2 hover:text-ink"
            >
              ← Back to history
            </button>
            <p className="text-sm text-ink truncate">{openedResult.resume_filename}</p>
            <p className="text-xs text-ink-soft truncate mb-6">{openedResult.jd_snippet}</p>
            <Report result={openedResult} />
          </div>
        )}

        {view === "compare" && comparePair && (
          <div>
            <button
              onClick={() => setView("history")}
              className="mb-6 text-sm text-ink-soft underline underline-offset-2 hover:text-ink"
            >
              ← Back to history
            </button>
            <CompareView a={comparePair[0]} b={comparePair[1]} />
          </div>
        )}
      </main>
    </div>
  );
}
