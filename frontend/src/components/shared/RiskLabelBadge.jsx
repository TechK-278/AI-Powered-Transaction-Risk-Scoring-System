import { findRiskTier } from "../../domain/riskTiers.js";

const TONE_CLASSES = {
  low: "bg-risk-low-soft text-risk-low-ink border-risk-low/30",
  medium: "bg-risk-medium-soft text-risk-medium-ink border-risk-medium/30",
  high: "bg-risk-high-soft text-risk-high-ink border-risk-high/30",
};

export default function RiskLabelBadge({ riskLabel }) {
  const tier = findRiskTier(riskLabel);
  const toneClass = tier ? TONE_CLASSES[tier.tone] : "bg-canvas text-ink-muted border-line";

  return (
    <span className={`inline-block rounded border px-1.5 py-0.5 text-xs font-semibold ${toneClass}`}>
      {riskLabel}
    </span>
  );
}
