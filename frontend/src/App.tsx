import { Navigate, Route, Routes } from "react-router-dom";

import AppLayout from "./components/Layout";
import { RequireProject } from "./components/RequireProject";
import { ProjectProvider } from "./context/ProjectContext";
import ComplianceMatrixPage from "./pages/ComplianceMatrixPage";
import Dashboard from "./pages/Dashboard";
import ExportScreen from "./pages/ExportScreen";
import ExtractedRequirements from "./pages/ExtractedRequirements";
import ProjectCreation from "./pages/ProjectCreation";
import ProposalEditor from "./pages/ProposalEditor";
import ScoringDashboard from "./pages/ScoringDashboard";
import Workspace from "./pages/Workspace";

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  return <RequireProject>{children}</RequireProject>;
}

export default function App() {
  return (
    <ProjectProvider>
      <Routes>
        <Route element={<AppLayout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="projects/new" element={<ProjectCreation />} />

          <Route
            path="workspace"
            element={
              <ProtectedRoute>
                <Workspace />
              </ProtectedRoute>
            }
          />
          <Route
            path="requirements"
            element={
              <ProtectedRoute>
                <ExtractedRequirements />
              </ProtectedRoute>
            }
          />
          <Route
            path="compliance"
            element={
              <ProtectedRoute>
                <ComplianceMatrixPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="scoring"
            element={
              <ProtectedRoute>
                <ScoringDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="proposal"
            element={
              <ProtectedRoute>
                <ProposalEditor />
              </ProtectedRoute>
            }
          />
          <Route
            path="export"
            element={
              <ProtectedRoute>
                <ExportScreen />
              </ProtectedRoute>
            }
          />
        </Route>
      </Routes>
    </ProjectProvider>
  );
}
