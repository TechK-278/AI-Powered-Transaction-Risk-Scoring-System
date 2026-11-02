import { RISK_TIERS } from "../../domain/riskTiers.js";

const SEGMENT_CLASSES = {
  low: "bg-risk-low",
  medium: "bg-risk-medium",
  high: "bg-risk-high",
};

const SCORE_POINTS = 101;

function tierWidthPercent(tier) {
  return `${((tier.maxScore - tier.minScore + 1) / SCORE_POINTS) * 100}%`;
}

/** Horizontal 0–100 scale showing the tier bands and where a score falls. */
export default function RiskScoreScale({ riskScore }) {
  return (
    <div role="img" aria-label={`Risk score ${riskScore} on a scale from 0 to 100`}>
      <div className="relative">
        <div className="flex h-2 overflow-hidden rounded-sm">
          {RISK_TIERS.map((tier) => (
            <div
              key={tier.label}
              className={`${SEGMENT_CLASSES[tier.tone]} opacity-80`}
              style={{ width: tierWidthPercent(tier) }}
            />
          ))}
        </div>
        <div
          className="absolute -top-1 h-4 w-0.5 -translate-x-1/2 bg-ink"
          style={{ left: `${((riskScore + 0.5) / SCORE_POINTS) * 100}%` }}
        />
      </div>
      <div className="mt-1 flex text-xs text-ink-muted">
        {RISK_TIERS.map((tier) => (
          <span key={tier.label} style={{ width: tierWidthPercent(tier) }}>
            {tier.label} {tier.minScore}–{tier.maxScore}
          </span>
        ))}
      </div>
    </div>
  );
}
