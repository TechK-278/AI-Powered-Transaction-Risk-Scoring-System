import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

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
import { RISK_TIERS } from "../../domain/riskTiers.js";

const dayLabelFormatter = new Intl.DateTimeFormat(undefined, { month: "short", day: "numeric", timeZone: "UTC" });

function formatDayLabel(isoDay) {
  return dayLabelFormatter.format(new Date(`${isoDay}T00:00:00Z`));
}

function VolumeTooltip({ active, payload }) {
  if (!active || !payload?.length) {
    return null;
  }
  const dayRow = payload[0].payload;
  const tierRows = [...RISK_TIERS].reverse().map((tier) => ({
    key: tier.tone,
    label: tier.label,
    value: dayRow[tier.tone].toLocaleString(),
    markColor: tier.markColor,
  }));
  const total = dayRow.low + dayRow.medium + dayRow.high;
  return (
    <ChartTooltipCard
      title={`${formatDayLabel(dayRow.day)} (UTC)`}
      rows={[...tierRows, { key: "total", label: "Total", value: total.toLocaleString() }]}
    />
  );
}

/** Evaluations per UTC day, stacked by risk tier (Low at the baseline). */
export default function DailyEvaluationVolumeChart({ dailyVolume, windowDays }) {
  const topTone = RISK_TIERS[RISK_TIERS.length - 1].tone;

  return (
    <section className="panel" aria-labelledby="volume-title">
      <div className="panel-header">
        <div>
          <h2 id="volume-title" className="panel-title">
            Daily evaluation volume
          </h2>
          <p className="text-xs text-ink-muted">Last {windowDays} days (UTC), by risk tier</p>
        </div>
      </div>
      <div className="space-y-3 p-4">
        <RiskTierLegend />
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={dailyVolume} margin={CHART_MARGIN} accessibilityLayer>
              <CartesianGrid {...GRID_PROPS} />
              <XAxis dataKey="day" tickFormatter={formatDayLabel} {...AXIS_PROPS} minTickGap={12} />
              <YAxis {...AXIS_PROPS} allowDecimals={false} axisLine={false} />
              <Tooltip content={<VolumeTooltip />} cursor={HOVER_CURSOR} />
              {RISK_TIERS.map((tier) => (
                <Bar
                  key={tier.tone}
                  dataKey={tier.tone}
                  name={tier.label}
                  stackId="tiers"
                  fill={tier.markColor}
                  stroke="var(--color-surface)"
                  strokeWidth={2}
                  maxBarSize={BAR_MAX_WIDTH}
                  radius={tier.tone === topTone ? BAR_TOP_RADIUS : 0}
                />
              ))}
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </section>
  );
}
