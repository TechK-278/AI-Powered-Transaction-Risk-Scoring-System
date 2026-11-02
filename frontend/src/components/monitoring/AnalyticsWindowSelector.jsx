export const ANALYTICS_WINDOW_OPTIONS = [7, 14, 30];

/** Segmented control for the number of days shown in the daily volume chart. */
export default function AnalyticsWindowSelector({ windowDays, onWindowChange }) {
  return (
    <div role="group" aria-label="Daily volume window" className="inline-flex rounded border border-line-strong">
      {ANALYTICS_WINDOW_OPTIONS.map((optionDays) => {
        const isActive = optionDays === windowDays;
        return (
          <button
            key={optionDays}
            type="button"
            aria-pressed={isActive}
            className={`px-3 py-1.5 text-sm first:rounded-l last:rounded-r ${
              isActive ? "bg-accent text-white" : "bg-surface text-ink hover:bg-canvas"
            }`}
            onClick={() => onWindowChange(optionDays)}
          >
            {optionDays}d
          </button>
        );
      })}
    </div>
  );
}
