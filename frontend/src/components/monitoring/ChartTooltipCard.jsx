/**
 * Tooltip body shared by the monitoring charts.
 * `rows` is a list of { key, label, value, markColor? } entries.
 */
export default function ChartTooltipCard({ title, rows }) {
  return (
    <div className="rounded border border-line bg-surface px-3 py-2 text-xs shadow-sm">
      <p className="mb-1 font-semibold text-ink">{title}</p>
      <dl className="grid grid-cols-[auto_auto] gap-x-4 gap-y-0.5">
        {rows.map((row) => (
          <div key={row.key} className="contents">
            <dt className="flex items-center gap-1.5 text-ink-muted">
              {row.markColor && (
                <span className="inline-block size-2 rounded-sm" style={{ backgroundColor: row.markColor }} aria-hidden="true" />
              )}
              {row.label}
            </dt>
            <dd className="numeric text-right text-ink">{row.value}</dd>
          </div>
        ))}
      </dl>
    </div>
  );
}
