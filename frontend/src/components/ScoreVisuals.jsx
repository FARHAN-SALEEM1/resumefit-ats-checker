import { useEffect, useState } from "react";

/** Counts up from 0 to `target` once, on mount / when target changes. */
export function useCountUp(target, durationMs = 900) {
  const [value, setValue] = useState(0);

  useEffect(() => {
    let frame;
    const start = performance.now();
    const from = 0;

    function tick(now) {
      const elapsed = now - start;
      const progress = Math.min(1, elapsed / durationMs);
      // ease-out cubic — quick start, gentle settle
      const eased = 1 - Math.pow(1 - progress, 3);
      setValue(from + (target - from) * eased);
      if (progress < 1) frame = requestAnimationFrame(tick);
    }
    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [target, durationMs]);

  return value;
}

function toneFor(score) {
  if (score >= 70) return { bar: "bg-teal", text: "text-teal" };
  if (score >= 45) return { bar: "bg-amber", text: "text-amber" };
  return { bar: "bg-rust", text: "text-rust" };
}

export function ScoreBar({ label, value }) {
  const tone = toneFor(value ?? 0);
  return (
    <div className="mb-3">
      <div className="flex justify-between text-sm mb-1">
        <span className="text-ink-soft">{label}</span>
        <span className={`font-medium ${tone.text}`}>
          {value === null || value === undefined ? "—" : `${Math.round(value)}%`}
        </span>
      </div>
      <div className="h-1.5 bg-line rounded-full overflow-hidden">
        <div
          className={`h-full ${tone.bar} rounded-full transition-all duration-700`}
          style={{ width: `${value ?? 0}%` }}
        />
      </div>
    </div>
  );
}
