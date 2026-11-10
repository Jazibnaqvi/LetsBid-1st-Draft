import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { useProject } from "../context/ProjectContext";
import PageHeader from "../components/ui/PageHeader";

export default function ProjectCreation() {
  const { createProject } = useProject();
  const navigate = useNavigate();

  const [name, setName] = useState("");
  const [clientName, setClientName] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file || !name.trim()) return;

    setLoading(true);
    setError(null);

    try {
      await createProject(name.trim(), clientName.trim(), file);
      navigate("/workspace");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create project");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-2xl">
      <PageHeader
        title="Create Project"
        description="Upload an RFP or bid document to start the analysis pipeline."
      />

      <form
        onSubmit={handleSubmit}
        className="rounded-xl border border-slate-200 bg-white p-8 shadow-sm"
      >
        <div className="space-y-5">
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-slate-700">
              Project Name
            </label>
            <input
              id="name"
              type="text"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. National Health RFP 2026"
              className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 text-sm shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
            />
          </div>

          <div>
            <label htmlFor="client" className="block text-sm font-medium text-slate-700">
              Client / Organization
            </label>
            <input
              id="client"
              type="text"
              value={clientName}
              onChange={(e) => setClientName(e.target.value)}
              placeholder="e.g. Ministry of Health"
              className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 text-sm shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
            />
          </div>

          <div>
            <label htmlFor="file" className="block text-sm font-medium text-slate-700">
              RFP Document
            </label>
            <input
              id="file"
              type="file"
              required
              accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
              className="mt-1 block w-full text-sm text-slate-600 file:mr-4 file:rounded-md file:border-0 file:bg-brand-600 file:px-4 file:py-2 file:text-sm file:font-medium file:text-white hover:file:bg-brand-700"
            />
            <p className="mt-1 text-xs text-slate-500">Supported: PDF, DOCX</p>
          </div>
        </div>

        {error && (
          <div className="mt-4 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {error}
          </div>
        )}

        <div className="mt-6 flex items-center gap-3">
          <button
            type="submit"
            disabled={loading || !file || !name.trim()}
            className="rounded-md bg-brand-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading ? "Analyzing document…" : "Create & Analyze"}
          </button>
          {loading && (
            <p className="text-sm text-slate-500">
              Running ingestion, NER, RAG matching, and proposal generation…
            </p>
          )}
        </div>
      </form>
    </div>
  );
}
