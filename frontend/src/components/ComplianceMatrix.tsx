import { useState } from "react";

interface ComplianceRow {
  row_id: number;
  requirement_text: string;
  source_quote: string;
  status: "Pass" | "Fail" | "Partial";
  matched_capability_id: string | null;
  matched_capability_title: string | null;
  evidence_text: string | null;
  proof_document: string | null;
  similarity_score: number | null;
  missing_capability: boolean;
  missing_proof: boolean;
  notes: string;
}

interface ComplianceMatrixProps {
  rows: ComplianceRow[];
  summary: Record<string, number>;
}

const STATUS_STYLES = {
  Pass: "bg-green-100 text-green-800",
  Fail: "bg-red-100 text-red-800",
  Partial: "bg-amber-100 text-amber-800",
};

export default function ComplianceMatrix({ rows, summary }: ComplianceMatrixProps) {
  const [evidenceRow, setEvidenceRow] = useState<ComplianceRow | null>(null);

  return (
    <div>
      <div className="mb-4 flex flex-wrap gap-3">
        {Object.entries(summary).map(([status, count]) => (
          <span
            key={status}
            className={`rounded-full px-3 py-1 text-sm font-semibold ${STATUS_STYLES[status as keyof typeof STATUS_STYLES]}`}
          >
            {status}: {count}
          </span>
        ))}
      </div>

      <div className="overflow-x-auto rounded-lg border border-slate-200">
        <table className="min-w-full divide-y divide-slate-200 text-sm">
          <thead className="bg-slate-50">
            <tr>
              <th className="px-4 py-3 text-left font-medium text-slate-600">Requirement</th>
              <th className="px-4 py-3 text-left font-medium text-slate-600">Matched Capability</th>
              <th className="px-4 py-3 text-left font-medium text-slate-600">Status</th>
              <th className="px-4 py-3 text-left font-medium text-slate-600">Gaps</th>
              <th className="px-4 py-3 text-left font-medium text-slate-600">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 bg-white">
            {rows.map((row) => (
              <tr
                key={row.row_id}
                className={
                  row.missing_capability || row.missing_proof ? "bg-red-50/40" : ""
                }
              >
                <td className="px-4 py-3 align-top">
                  <p className="font-medium text-slate-900">{row.requirement_text}</p>
                  <p className="mt-1 text-xs text-slate-500 italic">
                    "{row.source_quote.slice(0, 100)}
                    {row.source_quote.length > 100 ? "…" : ""}"
                  </p>
                </td>
                <td className="px-4 py-3 align-top">
                  {row.matched_capability_title ? (
                    <div>
                      <p className="font-medium text-slate-800">{row.matched_capability_title}</p>
                      <p className="text-xs text-slate-500">{row.matched_capability_id}</p>
                      {row.similarity_score != null && (
                        <p className="text-xs text-slate-500">
                          Match: {(row.similarity_score * 100).toFixed(0)}%
                        </p>
                      )}
                    </div>
                  ) : (
                    <span className="text-red-600">No match</span>
                  )}
                </td>
                <td className="px-4 py-3 align-top">
                  <span
                    className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${STATUS_STYLES[row.status]}`}
                  >
                    {row.status}
                  </span>
                </td>
                <td className="px-4 py-3 align-top text-xs">
                  {row.missing_capability && (
                    <span className="block font-medium text-red-600">Missing capability</span>
                  )}
                  {row.missing_proof && (
                    <span className="block font-medium text-amber-600">Missing proof</span>
                  )}
                  {!row.missing_capability && !row.missing_proof && (
                    <span className="text-green-600">Complete</span>
                  )}
                </td>
                <td className="px-4 py-3 align-top">
                  <button
                    type="button"
                    onClick={() => setEvidenceRow(row)}
                    disabled={!row.evidence_text}
                    className="rounded-md bg-slate-100 px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-200 disabled:opacity-40"
                  >
                    View Evidence
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {evidenceRow && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
          <div className="max-h-[80vh] w-full max-w-lg overflow-y-auto rounded-xl bg-white p-6 shadow-xl">
            <h4 className="text-lg font-semibold text-slate-900">Evidence Details</h4>
            <p className="mt-2 text-sm font-medium text-slate-700">{evidenceRow.requirement_text}</p>
            <p className="mt-3 text-sm text-slate-600">{evidenceRow.evidence_text}</p>
            {evidenceRow.proof_document && (
              <p className="mt-3 text-sm">
                <span className="font-medium text-slate-700">Proof:</span>{" "}
                {evidenceRow.proof_document}
              </p>
            )}
            <button
              type="button"
              onClick={() => setEvidenceRow(null)}
              className="mt-4 rounded-md bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
