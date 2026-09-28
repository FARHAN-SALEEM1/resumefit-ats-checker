export function Pill({ children, tone }) {
  const toneClasses =
    tone === "matched"
      ? "bg-teal-soft text-teal border-teal/30"
      : "bg-amber-soft text-amber border-amber/30";
  return (
    <span className={`inline-block text-xs px-2.5 py-1 rounded-full border mr-2 mb-2 ${toneClasses}`}>
      {children}
    </span>
  );
}

export default function SkillGap({ skillGap }) {
  const { matched_skills, missing_skills } = skillGap;

  return (
    <div className="border-t border-line pt-5">
      <p className="font-serif text-lg mb-3">Skills</p>

      {missing_skills.length > 0 && (
        <div className="mb-4">
          <p className="text-sm text-ink-soft mb-2">
            The job description asks for these, not found in your resume:
          </p>
          <div>
            {missing_skills.map((skill) => (
              <Pill key={skill} tone="missing">{skill}</Pill>
            ))}
          </div>
        </div>
      )}

      {matched_skills.length > 0 && (
        <div>
          <p className="text-sm text-ink-soft mb-2">Already covered in your resume:</p>
          <div>
            {matched_skills.map((skill) => (
              <Pill key={skill} tone="matched">{skill}</Pill>
            ))}
          </div>
        </div>
      )}

      {matched_skills.length === 0 && missing_skills.length === 0 && (
        <p className="text-sm text-ink-soft">
          No specific skills could be matched — the job description may not list
          concrete technical requirements.
        </p>
      )}
    </div>
  );
}
