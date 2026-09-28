import { useEffect, useState } from "react";
import { listAnalyses, getAnalysis } from "../api.js";

function formatDate(value) {
  if (!value) return "";
  // SQLite timestamps come back without a timezone; treat them as UTC.
  const iso = /Z|[+-]\d{2}:?\d{2}$/.test(value) ? value : `${value}Z`;
  const d = new Date(iso);
  if (isNaN(d)) return "";
  return d.toLocaleDateString(undefined, { day: "numeric", month: "short", year: "numeric" });
}

function scoreTone(score) {
  if (score >= 70) return "text-teal";
  if (score >= 45) return "text-amber";
  return "text-rust";
}

export default function HistoryView({ onOpen, onCompare }) {
  const [items, setItems] = useState(null);
  const [error, setError] = useState("");
  const [selected, setSelected] = useState([]);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    listAnalyses()
      .then(setItems)
      .catch((e) => setError(e.message || "Could not load history."));
  }, []);

  function toggle(id) {
    setSelected((prev) => {
      if (prev.includes(id)) return prev.filter((x) => x !== id);
      if (prev.length >= 2) return [prev[1], id]; // keep the two most recent picks
      return [...prev, id];
    });
  }

  async function open(id) {
    setBusy(true);
    setError("");
    try {
      onOpen(await getAnalysis(id));
    } catch (e) {
      setError(e.message || "Could not open this analysis.");
      setBusy(false);
    }
  }

  async function compare() {
    setBusy(true);
    setError("");
    try {
      const [a, b] = await Promise.all(selected.map(getAnalysis));
      onCompare(a, b);
    } catch (e) {
      setError(e.message || "Could not load the analyses to compare.");
      setBusy(false);
    }
  }

  if (error && !items) return <p className="text-sm text-rust">{error}</p>;
  if (!items) return <p className="text-sm text-ink-soft">Loading history…</p>;

  if (items.length === 0) {
    return (
      <p className="text-sm text-ink-soft">
        No analyses yet. Run a check and it will show up here.
      </p>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-4 gap-4">
        <p className="text-sm text-ink-soft">
          Tick any two to compare them side by side.
        </p>
        <button
          onClick={compare}
          disabled={selected.length !== 2 || busy}
          className="text-sm border border-ink px-3 py-1.5 rounded-sm shrink-0
            disabled:opacity-30 disabled:cursor-not-allowed
            hover:bg-ink hover:text-paper transition-colors"
        >
          Compare
        </button>
      </div>

      {error && <p className="text-sm text-rust mb-3">{error}</p>}

      <ul className="border-t border-line">
        {items.map((item) => (
          <li key={item.id} className="border-b border-line py-3 flex items-start gap-3">
            <input
              type="checkbox"
              checked={selected.includes(item.id)}
              onChange={() => toggle(item.id)}
              aria-label={`Select analysis ${item.id} for comparison`}
              className="mt-2 accent-teal"
            />
            <button
              onClick={() => open(item.id)}
              disabled={busy}
              className="flex-1 text-left flex items-baseline gap-4 min-w-0"
            >
              <span className={`font-serif text-2xl tabular-nums w-12 shrink-0 ${scoreTone(item.score)}`}>
                {Math.round(item.score)}
              </span>
              <span className="min-w-0">
                <span className="block text-sm text-ink truncate">{item.resume_filename}</span>
                <span className="block text-xs text-ink-soft truncate">{item.jd_snippet}</span>
              </span>
              <span className="ml-auto text-xs text-ink-soft shrink-0">{formatDate(item.created_at)}</span>
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
