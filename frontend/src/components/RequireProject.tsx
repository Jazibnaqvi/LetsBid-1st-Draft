import { Navigate } from "react-router-dom";

import { useProject } from "../context/ProjectContext";

export function RequireProject({ children }: { children: React.ReactNode }) {
  const { activeProject } = useProject();

  if (!activeProject) {
    return <Navigate to="/projects/new" replace />;
  }

  if (activeProject.status === "analyzing") {
    return (
      <div className="flex flex-col items-center justify-center py-24">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-brand-200 border-t-brand-600" />
        <p className="mt-4 text-sm text-slate-600">Analysis in progress…</p>
      </div>
    );
  }

  if (activeProject.status === "error") {
    return (
      <div className="mx-auto max-w-lg rounded-xl border border-red-200 bg-red-50 p-8 text-center">
        <h2 className="text-lg font-semibold text-red-900">Analysis Failed</h2>
        <p className="mt-2 text-sm text-red-700">{activeProject.errorMessage}</p>
      </div>
    );
  }

  if (!activeProject.analysis) {
    return <Navigate to="/projects/new" replace />;
  }

  return <>{children}</>;
}
