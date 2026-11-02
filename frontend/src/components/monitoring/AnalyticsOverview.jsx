import DailyEvaluationVolumeChart from "./DailyEvaluationVolumeChart.jsx";
import RiskDistributionChart from "./RiskDistributionChart.jsx";
import TransactionSummary from "./TransactionSummary.jsx";
import RequestErrorNotice from "../shared/RequestErrorNotice.jsx";

/** Summary figures and charts built from the analytics summary endpoint. */
export default function AnalyticsOverview({ analyticsQuery }) {
  const { status, data: summary, errorMessage } = analyticsQuery;

  if (status === "failed") {
    return <RequestErrorNotice message={errorMessage} />;
  }
  if (!summary) {
    return <p className="text-ink-muted">Loading analytics…</p>;
  }

  return (
    <div className="space-y-4" aria-busy={status === "loading"}>
      <TransactionSummary summary={summary} />
      <div className="grid gap-4 lg:grid-cols-2">
        <RiskDistributionChart scoreDistribution={summary.score_distribution} />
        <DailyEvaluationVolumeChart dailyVolume={summary.daily_volume} windowDays={summary.window_days} />
      </div>
    </div>
  );
}
