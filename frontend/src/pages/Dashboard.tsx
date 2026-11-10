import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { api } from "../api/client";
import { useProject } from "../context/ProjectContext";
import PageHeader from "../components/ui/PageHeader";
import StatCard from "../components/ui/StatCard";
import EmptyState from "../components/ui/EmptyState";

export default function Dashboard() {
  const { projects, setActiveProjectId } = useProject();
  const navigate = useNavigate();
  const [apiStatus, setApiStatus] = useState("checking...");

  useEffect(() => {
    api.health().then((r) => setApiStatus(r.status)).catch(() => setApiStatus("offline"));
  }, []);

  const readyProjects = projects.filter((p) => p.status === "ready");
  const totalRequirements = readyProjects.reduce(
    (sum, p) => sum + (p.analysis?.rag.total_requirements ?? 0),
    0,
  );

  return (
    <div>
      <PageHeader
        title="Dashboard"
        description="Overview of bid opportunities and analysis pipeline status."
        actions={
          <Link
            to="/projects/new"
            className="rounded-md bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700"
          >
            New Project
          </Link>
        }
      />

      <div className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Total Projects" value={projects.length} />
        <StatCard label="Ready for Review" value={readyProjects.length} accent="success" />
        <StatCard label="Requirements Analyzed" value={totalRequirements} />
        <StatCard
          label="API Status"
          value={apiStatus === "ok" ? "Online" : apiStatus}
          accent={apiStatus === "ok" ? "success" : "warning"}
        />
      </div>

      <section className="rounded-xl border border-slate-200 bg-white shadow-sm">
        <div className="border-b border-slate-200 px-6 py-4">
          <h2 className="font-semibold text-slate-900">Recent Projects</h2>
        </div>

        {projects.length === 0 ? (
          <div className="p-6">
            <EmptyState
              title="No projects yet"
              description="Create a new project by uploading an RFP document to begin analysis."
              actionLabel="Create Project"
              actionTo="/projects/new"
            />
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-200 text-sm">
              <thead className="bg-slate-50">
                <tr>
                  <th className="px-6 py-3 text-left font-medium text-slate-500">Project</th>
                  <th className="px-6 py-3 text-left font-medium text-slate-500">Client</th>
                  <th className="px-6 py-3 text-left font-medium text-slate-500">Document</th>
                  <th className="px-6 py-3 text-left font-medium text-slate-500">Status</th>
                  <th className="px-6 py-3 text-left font-medium text-slate-500">Score</th>
                  <th className="px-6 py-3 text-left font-medium text-slate-500">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {projects.map((project) => (
                  <tr key={project.id} className="hover:bg-slate-50">
                    <td className="px-6 py-4 font-medium text-slate-900">{project.name}</td>
                    <td className="px-6 py-4 text-slate-600">{project.clientName || "—"}</td>
                    <td className="px-6 py-4 text-slate-600">{project.fileName}</td>
                    <td className="px-6 py-4">
                      <span
                        className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${
                          project.status === "ready"
                            ? "bg-green-100 text-green-700"
                            : project.status === "error"
                              ? "bg-red-100 text-red-700"
                              : "bg-amber-100 text-amber-700"
                        }`}
                      >
                        {project.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-slate-600">
                      {project.analysis?.go_nogo.score.toFixed(0) ?? "—"}
                    </td>
                    <td className="px-6 py-4">
                      <button
                        type="button"
                        onClick={() => {
                          setActiveProjectId(project.id);
                          navigate("/workspace");
                        }}
                        className="font-medium text-brand-600 hover:text-brand-700"
                      >
                        Open →
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
