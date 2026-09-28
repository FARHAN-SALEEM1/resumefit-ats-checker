import { ScoreBar } from "./ScoreVisuals.jsx";
import { Pill } from "./SkillGap.jsx";

function Column({ result }) {
  return (
    <div className="min-w-0">
      <p className="text-sm text-ink truncate font-medium">{result.resume_filename}</p>
      <p className="text-xs text-ink-soft truncate mb-3">{result.jd_snippet}</p>

      <p className="font-serif text-5xl tabular-nums mb-4">
        {Math.round(result.overall_score)}
        <span className="text-base text-ink-soft"> / 100</span>
      </p>

      <ScoreBar label="Keyword & content" value={result.breakdown.keyword_match} />
      <ScoreBar label="Experience" value={result.breakdown.experience_match} />
      <ScoreBar label="ATS formatting" value={result.breakdown.formatting_score} />

      <div className="mt-4">
        <p className="text-xs text-ink-soft mb-2">Missing skills</p>
        {result.skill_gap.missing_skills.length === 0 ? (
          <p className="text-xs text-ink-soft">None detected</p>
        ) : (
          result.skill_gap.missing_skills.map((s) => <Pill key={s} tone="missing">{s}</Pill>)
        )}
      </div>
      <div className="mt-2">
        <p className="text-xs text-ink-soft mb-2">Matched skills</p>
        {result.skill_gap.matched_skills.length === 0 ? (
          <p className="text-xs text-ink-soft">None detected</p>
        ) : (
          result.skill_gap.matched_skills.map((s) => <Pill key={s} tone="matched">{s}</Pill>)
        )}
      </div>
    </div>
  );
}

export default function CompareView({ a, b }) {
  const diff = Math.round(a.overall_score) - Math.round(b.overall_score);
  let summary = "Both score the same overall.";
  if (diff > 0) summary = `The left one scores ${diff} point${diff === 1 ? "" : "s"} higher.`;
  if (diff < 0) summary = `The right one scores ${-diff} point${diff === -1 ? "" : "s"} higher.`;

  return (
    <div>
      <p className="text-sm text-ink-soft mb-6">{summary}</p>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-8">
        <Column result={a} />
        <Column result={b} />
      </div>
    </div>
  );
}
