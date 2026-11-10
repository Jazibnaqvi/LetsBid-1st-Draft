import { useState } from "react";

import { api, type ProposalSection } from "../api/client";

interface ProposalDraftProps {
  proposalId: string;
  documentName: string;
  sections: ProposalSection[];
  onUpdate: (sections: ProposalSection[]) => void;
}

export default function ProposalDraft({
  proposalId,
  documentName,
  sections,
  onUpdate,
}: ProposalDraftProps) {
  const [activeSection, setActiveSection] = useState(sections[0]?.section_id ?? "");
  const [editText, setEditText] = useState("");
  const [exportContent, setExportContent] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const current = sections.find((s) => s.section_id === activeSection);

  const startEdit = () => {
    if (!current) return;
    setEditText(current.edited_content ?? current.draft_content);
  };

  const saveEdit = async () => {
    if (!current) return;
    setBusy(true);
    try {
      const updated = await api.updateProposalSection(proposalId, current.section_id, editText);
      onUpdate(
        sections.map((s) => (s.section_id === updated.section_id ? updated : s)),
      );
    } finally {
      setBusy(false);
    }
  };

  const approveSection = async () => {
    if (!current) return;
    setBusy(true);
    try {
      const updated = await api.approveProposalSection(proposalId, current.section_id);
      onUpdate(
        sections.map((s) => (s.section_id === updated.section_id ? updated : s)),
      );
    } finally {
      setBusy(false);
    }
  };

  const handleExport = async () => {
    setBusy(true);
    try {
      const exported = await api.exportProposal(proposalId);
      setExportContent(exported.content);
    } finally {
      setBusy(false);
    }
  };

  const downloadExport = () => {
    if (!exportContent) return;
    const blob = new Blob([exportContent], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${documentName.replace(/\.[^.]+$/, "")}_proposal.md`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        {sections.map((section) => (
          <button
            key={section.section_id}
            type="button"
            onClick={() => setActiveSection(section.section_id)}
            className={`rounded-md px-3 py-1.5 text-sm font-medium ${
              activeSection === section.section_id
                ? "bg-brand-600 text-white"
                : "bg-slate-100 text-slate-700 hover:bg-slate-200"
            }`}
          >
            {section.title}
            {section.status === "approved" && " ✓"}
          </button>
        ))}
      </div>

      {current && (
        <div className="rounded-lg border border-slate-200 p-4">
          <div className="flex items-center justify-between">
            <h4 className="font-semibold text-slate-900">{current.title}</h4>
            <span
              className={`rounded-full px-2 py-0.5 text-xs font-semibold ${
                current.status === "approved"
                  ? "bg-green-100 text-green-800"
                  : "bg-slate-100 text-slate-600"
              }`}
            >
              {current.status}
            </span>
          </div>

          {current.evidence_refs.length > 0 && (
            <p className="mt-2 text-xs text-slate-500">
              Evidence: {current.evidence_refs.join(", ")}
            </p>
          )}

          <div className="mt-3 whitespace-pre-wrap text-sm text-slate-700">
            {current.edited_content ?? current.draft_content}
          </div>

          <textarea
            className="mt-4 w-full rounded-md border border-slate-300 p-3 text-sm"
            rows={6}
            placeholder="Edit section content..."
            value={editText}
            onChange={(e) => setEditText(e.target.value)}
            onFocus={startEdit}
          />

          <div className="mt-3 flex flex-wrap gap-2">
            <button
              type="button"
              onClick={saveEdit}
              disabled={busy || !editText}
              className="rounded-md bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50"
            >
              Save Edit
            </button>
            <button
              type="button"
              onClick={approveSection}
              disabled={busy}
              className="rounded-md bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-700 disabled:opacity-50"
            >
              Approve Section
            </button>
            <button
              type="button"
              onClick={handleExport}
              disabled={busy}
              className="rounded-md bg-slate-700 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-50"
            >
              Export Final
            </button>
            {exportContent && (
              <button
                type="button"
                onClick={downloadExport}
                className="rounded-md border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
              >
                Download .md
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
