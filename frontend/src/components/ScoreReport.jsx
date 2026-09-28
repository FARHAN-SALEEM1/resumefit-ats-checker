import { useCountUp, ScoreBar } from "./ScoreVisuals.jsx";

export default function ScoreReport({ result }) {
  const animatedScore = useCountUp(result.overall_score);

  return (
    <div>
      <div className="flex items-baseline gap-3 mb-6">
        <span className="font-serif text-6xl tabular-nums">
          {Math.round(animatedScore)}
        </span>
        <span className="text-ink-soft text-lg">/ 100 match score</span>
      </div>

      <div className="mb-6">
        <ScoreBar label="Keyword & content match" value={result.breakdown.keyword_match} />
        <ScoreBar label="Experience match" value={result.breakdown.experience_match} />
        <ScoreBar label="ATS formatting" value={result.breakdown.formatting_score} />
      </div>

      {result.ats_formatting?.issues?.length > 0 && (
        <div className="border-t border-line pt-4">
          <p className="text-sm font-medium text-ink mb-2">Formatting issues found</p>
          <ul className="space-y-1">
            {result.ats_formatting.issues.map((issue, i) => (
              <li key={i} className="text-sm text-ink-soft flex gap-2">
                <span className="text-amber">—</span>
                <span>{issue}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
