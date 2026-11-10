import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";

import type { AnalyzeResult, ProposalSection } from "../api/client";

export interface Project {
  id: string;
  name: string;
  clientName: string;
  fileName: string;
  createdAt: string;
  status: "draft" | "analyzing" | "ready" | "error";
  analysis: AnalyzeResult | null;
  errorMessage?: string;
}

interface ProjectContextValue {
  projects: Project[];
  activeProject: Project | null;
  activeProjectId: string | null;
  setActiveProjectId: (id: string | null) => void;
  createProject: (name: string, clientName: string, file: File) => Promise<string>;
  updateProposalSections: (sections: ProposalSection[]) => void;
  deleteProject: (id: string) => void;
}

const STORAGE_KEY = "letsbid_projects";
const ACTIVE_KEY = "letsbid_active_project";

const ProjectContext = createContext<ProjectContextValue | null>(null);

function loadProjects(): Project[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? (JSON.parse(raw) as Project[]) : [];
  } catch {
    return [];
  }
}

function saveProjects(projects: Project[]) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(projects));
}

export function ProjectProvider({ children }: { children: React.ReactNode }) {
  const [projects, setProjects] = useState<Project[]>(loadProjects);
  const [activeProjectId, setActiveProjectIdState] = useState<string | null>(
    () => localStorage.getItem(ACTIVE_KEY),
  );

  useEffect(() => {
    saveProjects(projects);
  }, [projects]);

  const setActiveProjectId = useCallback((id: string | null) => {
    setActiveProjectIdState(id);
    if (id) {
      localStorage.setItem(ACTIVE_KEY, id);
    } else {
      localStorage.removeItem(ACTIVE_KEY);
    }
  }, []);

  const activeProject = useMemo(
    () => projects.find((p) => p.id === activeProjectId) ?? null,
    [projects, activeProjectId],
  );

  const createProject = useCallback(
    async (name: string, clientName: string, file: File): Promise<string> => {
      const id = crypto.randomUUID();
      const project: Project = {
        id,
        name,
        clientName,
        fileName: file.name,
        createdAt: new Date().toISOString(),
        status: "analyzing",
        analysis: null,
      };

      setProjects((prev) => [project, ...prev]);
      setActiveProjectId(id);

      try {
        const { api } = await import("../api/client");
        const analysis = await api.analyzeDocument(file);
        setProjects((prev) =>
          prev.map((p) =>
            p.id === id ? { ...p, status: "ready", analysis, errorMessage: undefined } : p,
          ),
        );
      } catch (err) {
        const message = err instanceof Error ? err.message : "Analysis failed";
        setProjects((prev) =>
          prev.map((p) =>
            p.id === id ? { ...p, status: "error", errorMessage: message } : p,
          ),
        );
        throw err;
      }

      return id;
    },
    [setActiveProjectId],
  );

  const updateProposalSections = useCallback(
    (sections: ProposalSection[]) => {
      if (!activeProjectId) return;
      setProjects((prev) =>
        prev.map((p) => {
          if (p.id !== activeProjectId || !p.analysis) return p;
          return {
            ...p,
            analysis: {
              ...p.analysis,
              proposal: { ...p.analysis.proposal, sections },
            },
          };
        }),
      );
    },
    [activeProjectId],
  );

  const deleteProject = useCallback(
    (id: string) => {
      setProjects((prev) => prev.filter((p) => p.id !== id));
      if (activeProjectId === id) {
        setActiveProjectId(null);
      }
    },
    [activeProjectId, setActiveProjectId],
  );

  const value = useMemo(
    () => ({
      projects,
      activeProject,
      activeProjectId,
      setActiveProjectId,
      createProject,
      updateProposalSections,
      deleteProject,
    }),
    [
      projects,
      activeProject,
      activeProjectId,
      setActiveProjectId,
      createProject,
      updateProposalSections,
      deleteProject,
    ],
  );

  return <ProjectContext.Provider value={value}>{children}</ProjectContext.Provider>;
}

export function useProject() {
  const ctx = useContext(ProjectContext);
  if (!ctx) {
    throw new Error("useProject must be used within ProjectProvider");
  }
  return ctx;
}

export function useRequireProject() {
  const { activeProject } = useProject();
  return activeProject;
}
