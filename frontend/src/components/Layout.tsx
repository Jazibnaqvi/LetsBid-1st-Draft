import { NavLink, Outlet, useNavigate } from "react-router-dom";

import { useProject } from "../context/ProjectContext";

const MAIN_NAV = [
  { to: "/dashboard", label: "Dashboard", icon: "M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" },
  { to: "/projects/new", label: "New Project", icon: "M12 4v16m8-8H4" },
];

const WORKSPACE_NAV = [
  { to: "/workspace", label: "Workspace", end: true },
  { to: "/requirements", label: "Requirements" },
  { to: "/compliance", label: "Compliance Matrix" },
  { to: "/scoring", label: "Scoring" },
  { to: "/proposal", label: "Proposal Editor" },
  { to: "/export", label: "Export" },
];

function NavIcon({ d }: { d: string }) {
  return (
    <svg className="h-5 w-5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d={d} />
    </svg>
  );
}

export default function AppLayout() {
  const { activeProject, setActiveProjectId } = useProject();
  const navigate = useNavigate();

  const linkClass = ({ isActive }: { isActive: boolean }) =>
    `flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors ${
      isActive
        ? "bg-brand-600 text-white"
        : "text-slate-300 hover:bg-slate-800 hover:text-white"
    }`;

  const workspaceLinkClass = ({ isActive }: { isActive: boolean }) =>
    `block rounded-md px-3 py-2 text-sm transition-colors ${
      isActive
        ? "bg-slate-800 font-medium text-white"
        : "text-slate-400 hover:bg-slate-800/60 hover:text-slate-200"
    }`;

  return (
    <div className="flex min-h-screen bg-slate-100">
      <aside className="flex w-64 shrink-0 flex-col bg-slate-900 text-white">
        <div className="border-b border-slate-800 px-5 py-5">
          <div className="flex items-center gap-2">
            <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-600 text-sm font-bold">
              LB
            </span>
            <div>
              <p className="font-semibold tracking-tight">LetsBid</p>
              <p className="text-xs text-slate-400">Proposal Engine</p>
            </div>
          </div>
        </div>

        <nav className="flex-1 space-y-1 px-3 py-4">
          {MAIN_NAV.map((item) => (
            <NavLink key={item.to} to={item.to} className={linkClass}>
              <NavIcon d={item.icon} />
              {item.label}
            </NavLink>
          ))}

          {activeProject && (
            <div className="pt-4">
              <p className="mb-2 px-3 text-xs font-semibold uppercase tracking-wider text-slate-500">
                Active Project
              </p>
              <div className="mb-3 rounded-md bg-slate-800 px-3 py-2">
                <p className="truncate text-sm font-medium text-white">{activeProject.name}</p>
                <p className="truncate text-xs text-slate-400">{activeProject.fileName}</p>
              </div>
              <div className="space-y-0.5">
                {WORKSPACE_NAV.map((item) => (
                  <NavLink
                    key={item.to}
                    to={item.to}
                    end={item.end}
                    className={workspaceLinkClass}
                  >
                    {item.label}
                  </NavLink>
                ))}
              </div>
            </div>
          )}
        </nav>

        {activeProject && (
          <div className="border-t border-slate-800 p-3">
            <button
              type="button"
              onClick={() => {
                setActiveProjectId(null);
                navigate("/dashboard");
              }}
              className="w-full rounded-md px-3 py-2 text-left text-sm text-slate-400 hover:bg-slate-800 hover:text-white"
            >
              Close Project
            </button>
          </div>
        )}
      </aside>

      <div className="flex flex-1 flex-col">
        <header className="border-b border-slate-200 bg-white px-8 py-4">
          <div className="flex items-center justify-between">
            <p className="text-sm text-slate-500">
              Bid & Proposal Response Platform
            </p>
            {activeProject && (
              <span
                className={`rounded-full px-3 py-1 text-xs font-semibold ${
                  activeProject.status === "ready"
                    ? "bg-green-100 text-green-700"
                    : activeProject.status === "error"
                      ? "bg-red-100 text-red-700"
                      : "bg-amber-100 text-amber-700"
                }`}
              >
                {activeProject.status.toUpperCase()}
              </span>
            )}
          </div>
        </header>
        <main className="flex-1 overflow-auto p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
