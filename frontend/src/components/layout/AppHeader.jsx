export default function AppHeader({ children }) {
  return (
    <header className="border-b border-line bg-surface">
      <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-x-8 gap-y-2 px-4 py-3">
        <div>
          <p className="text-base font-semibold text-ink">Transaction Risk Console</p>
          <p className="text-xs text-ink-muted">XGBoost fraud model · risk scores 0–100</p>
        </div>
        {children}
      </div>
    </header>
  );
}
