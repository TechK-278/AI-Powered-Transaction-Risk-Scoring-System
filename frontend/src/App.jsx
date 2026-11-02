import { lazy, Suspense } from "react";

import AppHeader from "./components/layout/AppHeader.jsx";
import WorkspaceNavigation from "./components/layout/WorkspaceNavigation.jsx";
import { useHashWorkspace } from "./hooks/useHashWorkspace.js";
import EvaluationPage from "./pages/EvaluationPage.jsx";

// Loaded on demand: the charting library is only needed on the monitoring workspace.
const MonitoringPage = lazy(() => import("./pages/MonitoringPage.jsx"));

const WORKSPACES = [
  { key: "evaluate", label: "Evaluate" },
  { key: "monitor", label: "Monitor" },
];
const WORKSPACE_KEYS = WORKSPACES.map((workspace) => workspace.key);

export default function App() {
  const activeWorkspaceKey = useHashWorkspace(WORKSPACE_KEYS, "evaluate");

  return (
    <>
      <AppHeader>
        <WorkspaceNavigation workspaces={WORKSPACES} activeWorkspaceKey={activeWorkspaceKey} />
      </AppHeader>
      <main className="mx-auto max-w-7xl px-4 py-6">
        {activeWorkspaceKey === "monitor" ? (
          <Suspense fallback={<p className="text-ink-muted">Loading monitoring workspace…</p>}>
            <MonitoringPage />
          </Suspense>
        ) : (
          <EvaluationPage />
        )}
      </main>
    </>
  );
}
