import ScoreReport from "./ScoreReport.jsx";
import SkillGap from "./SkillGap.jsx";
import FeedbackPanel from "./FeedbackPanel.jsx";

// One full analysis report. Used both right after a new check and when
// reopening a past analysis from History.
export default function Report({ result }) {
  return (
    <div>
      <ScoreReport result={result} />
      <div className="mt-6">
        <SkillGap skillGap={result.skill_gap} />
      </div>
      <div className="mt-2">
        <FeedbackPanel key={result.analysis_id} resumeId={result.resume_id} jdId={result.jd_id} />
      </div>
    </div>
  );
}
