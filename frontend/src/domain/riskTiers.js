/**
 * Display metadata for the risk tiers produced by the backend RiskScoreEngine.
 * Boundaries mirror RiskScoreEngine.LOW_MAX (30) and MEDIUM_MAX (70); the
 * backend remains the source of truth for assigning a label.
 */
export const RISK_TIERS = [
  {
    label: "Low",
    minScore: 0,
    maxScore: 30,
    summary: "Lower modeled fraud risk",
    tone: "low",
  },
  {
    label: "Medium",
    minScore: 31,
    maxScore: 70,
    summary: "Moderate modeled fraud risk",
    tone: "medium",
  },
  {
    label: "High",
    minScore: 71,
    maxScore: 100,
    summary: "Higher modeled fraud risk",
    tone: "high",
  },
];

export const RISK_LABELS = RISK_TIERS.map((tier) => tier.label);

export function findRiskTier(riskLabel) {
  return RISK_TIERS.find((tier) => tier.label === riskLabel) ?? null;
}

export function findRiskTierForScore(riskScore) {
  return RISK_TIERS.find((tier) => riskScore >= tier.minScore && riskScore <= tier.maxScore) ?? null;
}
