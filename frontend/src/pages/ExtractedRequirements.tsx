import { useProject } from "../context/ProjectContext";
import EntityResults from "../components/EntityResults";
import PageHeader from "../components/ui/PageHeader";

export default function ExtractedRequirements() {
  const { activeProject } = useProject();
  const { entities } = activeProject!.analysis!.ner;
  const counts = activeProject!.analysis!.ner.metadata.entity_counts;

  return (
    <div>
      <PageHeader
        title="Extracted Requirements"
        description="Named entities extracted from the RFP via Gemini NER — separate from raw text ingestion."
      />

      <div className="mb-6 rounded-lg border border-slate-200 bg-white p-4 text-sm text-slate-600">
        Model: <span className="font-medium">{activeProject!.analysis!.ner.metadata.model}</span>
        {" · "}
        Total entities:{" "}
        <span className="font-medium">
          {Object.values(counts).reduce((a, b) => a + b, 0)}
        </span>
        {activeProject!.analysis!.ner.metadata.truncated && (
          <span className="ml-2 text-amber-600">(document truncated for processing)</span>
        )}
      </div>

      <EntityResults entities={entities} counts={counts} />
    </div>
  );
}
