import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import ChartTooltipCard from "./ChartTooltipCard.jsx";
import RiskTierLegend from "./RiskTierLegend.jsx";
import {
  AXIS_PROPS,
  BAR_MAX_WIDTH,
  BAR_TOP_RADIUS,
  CHART_MARGIN,
  GRID_PROPS,
  HOVER_CURSOR,
} from "./chartAppearance.js";
import { findRiskTierForScore } from "../../domain/riskTiers.js";

/** A range straddling a tier boundary (30–39, 70–79) takes the tier of most scores in it. */
function majorityTierColor(bucket) {
  const midpointScore = Math.floor((bucket.score_from + bucket.score_to) / 2);
  return findRiskTierForScore(midpointScore)?.markColor;
}

function DistributionTooltip({ active, payload }) {
  if (!active || !payload?.length) {
    return null;
  }
  const bucket = payload[0].payload;
  return (
    <ChartTooltipCard
      title={`Score ${bucket.score_from}–${bucket.score_to}`}
      rows={[{ key: "count", label: "Evaluations", value: bucket.count.toLocaleString(), markColor: majorityTierColor(bucket) }]}
    />
  );
}

/** Histogram of risk scores across all persisted evaluations. */
export default function RiskDistributionChart({ scoreDistribution }) {
  const chartRows = scoreDistribution.map((bucket) => ({
    ...bucket,
    rangeLabel: `${bucket.score_from}–${bucket.score_to}`,
  }));

  return (
    <section className="panel" aria-labelledby="distribution-title">
      <div className="panel-header">
        <div>
          <h2 id="distribution-title" className="panel-title">
            Risk score distribution
          </h2>
          <p className="text-xs text-ink-muted">All evaluations, in ten-point score ranges</p>
        </div>
      </div>
      <div className="space-y-3 p-4">
        <RiskTierLegend />
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartRows} margin={CHART_MARGIN} accessibilityLayer>
              <CartesianGrid {...GRID_PROPS} />
              <XAxis dataKey="rangeLabel" {...AXIS_PROPS} interval={0} />
              <YAxis {...AXIS_PROPS} allowDecimals={false} axisLine={false} />
              <Tooltip content={<DistributionTooltip />} cursor={HOVER_CURSOR} />
              <Bar dataKey="count" name="Evaluations" maxBarSize={BAR_MAX_WIDTH} radius={BAR_TOP_RADIUS}>
                {chartRows.map((bucket) => (
                  <Cell key={bucket.rangeLabel} fill={majorityTierColor(bucket)} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </section>
  );
}
