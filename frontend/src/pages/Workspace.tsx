import { Link } from "react-router-dom";

import { useProject } from "../context/ProjectContext";
import PageHeader from "../components/ui/PageHeader";
import StatCard from "../components/ui/StatCard";

const STEPS = [
  { to: "/requirements", label: "Extracted Requirements", desc: "Review NER-extracted entities" },
  { to: "/compliance", label: "Compliance Matrix", desc: "Match requirements to capabilities" },
  { to: "/scoring", label: "Scoring Dashboard", desc: "GO / NO-GO bid decision" },
  { to: "/proposal", label: "Proposal Editor", desc: "Review and edit draft sections" },
  { to: "/export", label: "Export", desc: "Download final proposal" },
];

export default function Workspace() {
  const { activeProject } = useProject();
  const analysis = activeProject!.analysis!;

  return (
    <div>
      <PageHeader
        title={activeProject!.name}
        description={`${activeProject!.clientName} · ${activeProject!.fileName}`}
      />

      <div className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Requirements" value={analysis.rag.total_requirements} />
        <StatCard
          label="RAG Matches"
          value={analysis.rag.matched_requirements}
          accent="success"
        />
        <StatCard
          label="Compliance Pass"
          value={analysis.compliance.summary.Pass ?? 0}
          accent="success"
        />
        <StatCard
          label="GO/NO-GO Score"
          value={analysis.go_nogo.score.toFixed(0)}
          subtext={analysis.go_nogo.recommendation}
          accent={
            analysis.go_nogo.recommendation === "GO"
              ? "success"
              : analysis.go_nogo.recommendation === "NO-GO"
                ? "danger"
                : "warning"
          }
        />
      </div>

      <section className="rounded-xl border border-slate-200 bg-white shadow-sm">
        <div className="border-b border-slate-200 px-6 py-4">
          <h2 className="font-semibold text-slate-900">Analysis Pipeline</h2>
          <p className="mt-1 text-sm text-slate-500">
            Navigate through each stage of the bid response workflow.
          </p>
        </div>
        <div className="grid gap-4 p-6 sm:grid-cols-2 lg:grid-cols-3">
          {STEPS.map((step, index) => (
            <Link
              key={step.to}
              to={step.to}
              className="group rounded-lg border border-slate-200 p-5 transition-shadow hover:border-brand-300 hover:shadow-md"
            >
              <span className="flex h-8 w-8 items-center justify-center rounded-full bg-brand-100 text-sm font-bold text-brand-700">
                {index + 1}
              </span>
              <h3 className="mt-3 font-semibold text-slate-900 group-hover:text-brand-600">
                {step.label}
              </h3>
              <p className="mt-1 text-sm text-slate-500">{step.desc}</p>
            </Link>
          ))}
        </div>
      </section>

      <section className="mt-6 rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="font-semibold text-slate-900">Document Summary</h2>
        <dl className="mt-4 grid gap-4 text-sm sm:grid-cols-2 lg:grid-cols-4">
          <div>
            <dt className="text-slate-500">File Type</dt>
            <dd className="font-medium">{analysis.ingestion.metadata.file_type.toUpperCase()}</dd>
          </div>
          <div>
            <dt className="text-slate-500">Pages</dt>
            <dd className="font-medium">{analysis.ingestion.metadata.page_count ?? "N/A"}</dd>
          </div>
          <div>
            <dt className="text-slate-500">Word Count</dt>
            <dd className="font-medium">{analysis.ingestion.metadata.word_count.toLocaleString()}</dd>
          </div>
          <div>
            <dt className="text-slate-500">Win Probability</dt>
            <dd className="font-medium">
              {(analysis.go_nogo.win_probability * 100).toFixed(0)}%
            </dd>
          </div>
        </dl>
      </section>
    </div>
  );
}
