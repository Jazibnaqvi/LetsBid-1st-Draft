import { useProject } from "../context/ProjectContext";
import ComplianceMatrix from "../components/ComplianceMatrix";
import PageHeader from "../components/ui/PageHeader";
import StatCard from "../components/ui/StatCard";

export default function ComplianceMatrixPage() {
  const { activeProject } = useProject();
  const { rows, summary } = activeProject!.analysis!.compliance;
  const rag = activeProject!.analysis!.rag;

  return (
    <div>
      <PageHeader
        title="Compliance Matrix"
        description="Requirement-to-capability mapping with evidence-backed pass/fail status."
      />

      <div className="mb-6 grid gap-4 sm:grid-cols-4">
        <StatCard label="Total Requirements" value={rag.total_requirements} />
        <StatCard label="Pass" value={summary.Pass ?? 0} accent="success" />
        <StatCard label="Partial" value={summary.Partial ?? 0} accent="warning" />
        <StatCard label="Fail" value={summary.Fail ?? 0} accent="danger" />
      </div>

      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <ComplianceMatrix rows={rows} summary={summary} />
      </div>
    </div>
  );
}
