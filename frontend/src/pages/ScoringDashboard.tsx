import { useProject } from "../context/ProjectContext";
import GoNoGoScore from "../components/GoNoGoScore";
import PageHeader from "../components/ui/PageHeader";

export default function ScoringDashboard() {
  const { activeProject } = useProject();
  const goNogo = activeProject!.analysis!.go_nogo;

  return (
    <div>
      <PageHeader
        title="Scoring Dashboard"
        description="Heuristic GO / NO-GO assessment based on domain, certification, client fit, and historical outcomes."
      />

      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <GoNoGoScore
          score={goNogo.score}
          win_probability={goNogo.win_probability}
          recommendation={goNogo.recommendation}
          factors={goNogo.factors}
          summary={goNogo.summary}
        />
      </div>
    </div>
  );
}
