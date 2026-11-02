import { useEffect, useState } from "react";

/**
 * Keeps the active workspace in the URL hash (e.g. "#monitor") so it survives
 * reloads and supports browser back/forward without a routing library.
 */
export function useHashWorkspace(workspaceKeys, defaultKey) {
  const readWorkspaceFromHash = () => {
    const hashKey = window.location.hash.replace("#", "");
    return workspaceKeys.includes(hashKey) ? hashKey : defaultKey;
  };

  const [activeWorkspaceKey, setActiveWorkspaceKey] = useState(readWorkspaceFromHash);

  useEffect(() => {
    const syncWorkspace = () => setActiveWorkspaceKey(readWorkspaceFromHash());
    window.addEventListener("hashchange", syncWorkspace);
    return () => window.removeEventListener("hashchange", syncWorkspace);
    // Subscribe once: callers pass module-level constants for the keys.
  }, []);

  return activeWorkspaceKey;
}
