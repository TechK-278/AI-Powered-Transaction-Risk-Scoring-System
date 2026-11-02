import { RISK_TIERS } from "../../domain/riskTiers.js";

/** Legend for charts whose marks are colored by risk tier. */
export default function RiskTierLegend() {
  return (
    <ul className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-ink-muted" aria-label="Legend">
      {RISK_TIERS.map((tier) => (
        <li key={tier.label} className="flex items-center gap-1.5">
          <span className="inline-block size-2.5 rounded-sm" style={{ backgroundColor: tier.markColor }} aria-hidden="true" />
          {tier.label} ({tier.minScore}–{tier.maxScore})
        </li>
      ))}
    </ul>
  );
}
