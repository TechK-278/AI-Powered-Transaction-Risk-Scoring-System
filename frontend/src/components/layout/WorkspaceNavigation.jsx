/** Primary navigation between console workspaces. `workspaces` is a list of { key, label }. */
export default function WorkspaceNavigation({ workspaces, activeWorkspaceKey }) {
  return (
    <nav aria-label="Workspaces">
      <ul className="flex gap-1">
        {workspaces.map((workspace) => {
          const isActive = workspace.key === activeWorkspaceKey;
          return (
            <li key={workspace.key}>
              <a
                href={`#${workspace.key}`}
                aria-current={isActive ? "page" : undefined}
                className={`block rounded px-3 py-1.5 text-sm font-medium ${
                  isActive ? "bg-accent-soft text-accent" : "text-ink-muted hover:bg-canvas hover:text-ink"
                }`}
              >
                {workspace.label}
              </a>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
