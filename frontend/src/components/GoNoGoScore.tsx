interface ScoreFactor {
  name: string;
  weight: number;
  score: number;
  weighted_score: number;
  rationale: string;
}

interface GoNoGoScoreProps {
  score: number;
  win_probability: number;
  recommendation: "GO" | "NO-GO" | "CONDITIONAL";
  factors: ScoreFactor[];
  summary: string;
}

const REC_STYLES = {
  GO: "bg-green-100 text-green-800 border-green-200",
  "NO-GO": "bg-red-100 text-red-800 border-red-200",
  CONDITIONAL: "bg-amber-100 text-amber-800 border-amber-200",
};

export default function GoNoGoScore({
  score,
  win_probability,
  recommendation,
  factors,
  summary,
}: GoNoGoScoreProps) {
  return (
    <div className="space-y-4">
      <div className="grid gap-4 sm:grid-cols-3">
        <div className="rounded-lg border border-slate-200 bg-slate-50 p-4 text-center">
          <p className="text-sm text-slate-500">Overall Score</p>
          <p className="text-3xl font-bold text-slate-900">{score.toFixed(1)}</p>
        </div>
        <div className="rounded-lg border border-slate-200 bg-slate-50 p-4 text-center">
          <p className="text-sm text-slate-500">Win Probability</p>
          <p className="text-3xl font-bold text-brand-600">
            {(win_probability * 100).toFixed(0)}%
          </p>
        </div>
        <div
          className={`rounded-lg border p-4 text-center ${REC_STYLES[recommendation]}`}
        >
          <p className="text-sm opacity-80">Recommendation</p>
          <p className="text-3xl font-bold">{recommendation}</p>
        </div>
      </div>

      <p className="text-sm text-slate-600">{summary}</p>

      <div className="space-y-2">
        {factors.map((factor) => (
          <div key={factor.name} className="rounded-lg border border-slate-200 p-3">
            <div className="flex items-center justify-between">
              <span className="font-medium text-slate-900">{factor.name}</span>
              <span className="text-sm text-slate-500">
                {(factor.score * 100).toFixed(0)}% × {(factor.weight * 100).toFixed(0)}% ={" "}
                {factor.weighted_score.toFixed(1)}
              </span>
            </div>
            <div className="mt-2 h-2 rounded-full bg-slate-100">
              <div
                className="h-2 rounded-full bg-brand-500"
                style={{ width: `${factor.score * 100}%` }}
              />
            </div>
            <p className="mt-2 text-xs text-slate-500">{factor.rationale}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
