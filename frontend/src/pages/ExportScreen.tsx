import { useState } from "react";

import { api } from "../api/client";
import { useProject } from "../context/ProjectContext";
import PageHeader from "../components/ui/PageHeader";
import StatCard from "../components/ui/StatCard";

export default function ExportScreen() {
  const { activeProject } = useProject();
  const proposal = activeProject!.analysis!.proposal;
  const sections = proposal.sections;

  const [exportContent, setExportContent] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const approvedCount = sections.filter((s) => s.status === "approved").length;

  const handleExport = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await api.exportProposal(proposal.proposal_id);
      setExportContent(result.content);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Export failed");
    } finally {
      setLoading(false);
    }
  };

  const downloadMarkdown = () => {
    if (!exportContent) return;
    const blob = new Blob([exportContent], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${activeProject!.name.replace(/\s+/g, "_")}_proposal.md`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const downloadJson = () => {
    const payload = {
      project: activeProject!.name,
      client: activeProject!.clientName,
      exported_at: new Date().toISOString(),
      analysis: activeProject!.analysis,
    };
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${activeProject!.name.replace(/\s+/g, "_")}_full_export.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div>
      <PageHeader
        title="Export"
        description="Generate and download the final proposal package."
        actions={
          <button
            type="button"
            onClick={handleExport}
            disabled={loading}
            className="rounded-md bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50"
          >
            {loading ? "Generating…" : "Generate Export"}
          </button>
        }
      />

      <div className="mb-6 grid gap-4 sm:grid-cols-3">
        <StatCard label="Total Sections" value={sections.length} />
        <StatCard
          label="Approved"
          value={approvedCount}
          accent={approvedCount === sections.length ? "success" : "warning"}
        />
        <StatCard
          label="Pending Review"
          value={sections.length - approvedCount}
          accent={approvedCount === sections.length ? "success" : "warning"}
        />
      </div>

      {approvedCount < sections.length && (
        <div className="mb-6 rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
          {sections.length - approvedCount} section(s) still in draft status. Review them in the
          Proposal Editor before final export.
        </div>
      )}

      {error && (
        <div className="mb-6 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}

      <section className="rounded-xl border border-slate-200 bg-white shadow-sm">
        <div className="border-b border-slate-200 px-6 py-4">
          <h2 className="font-semibold text-slate-900">Section Status</h2>
        </div>
        <ul className="divide-y divide-slate-100">
          {sections.map((section) => (
            <li key={section.section_id} className="flex items-center justify-between px-6 py-4">
              <div>
                <p className="font-medium text-slate-900">{section.title}</p>
                <p className="text-xs text-slate-500">
                  Evidence: {section.evidence_refs.join(", ") || "None"}
                </p>
              </div>
              <span
                className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${
                  section.status === "approved"
                    ? "bg-green-100 text-green-700"
                    : "bg-slate-100 text-slate-600"
                }`}
              >
                {section.status}
              </span>
            </li>
          ))}
        </ul>
      </section>

      {exportContent && (
        <section className="mt-6 rounded-xl border border-slate-200 bg-white shadow-sm">
          <div className="flex items-center justify-between border-b border-slate-200 px-6 py-4">
            <h2 className="font-semibold text-slate-900">Export Preview</h2>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={downloadMarkdown}
                className="rounded-md bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700"
              >
                Download .md
              </button>
              <button
                type="button"
                onClick={downloadJson}
                className="rounded-md border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
              >
                Download Full JSON
              </button>
            </div>
          </div>
          <pre className="max-h-96 overflow-auto whitespace-pre-wrap p-6 text-sm text-slate-700">
            {exportContent}
          </pre>
        </section>
      )}
    </div>
  );
}
