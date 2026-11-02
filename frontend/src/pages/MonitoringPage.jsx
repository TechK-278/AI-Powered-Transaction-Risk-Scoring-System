import { useState } from "react";

import AnalyticsOverview from "../components/monitoring/AnalyticsOverview.jsx";
import AnalyticsWindowSelector from "../components/monitoring/AnalyticsWindowSelector.jsx";
import EvaluationHistory from "../components/monitoring/EvaluationHistory.jsx";
import { useAnalyticsSummary } from "../hooks/useAnalyticsSummary.js";
import { useTransactionHistory } from "../hooks/useTransactionHistory.js";

/** Review risk trends across persisted evaluations and inspect individual records. */
export default function MonitoringPage() {
  const [windowDays, setWindowDays] = useState(14);
  const analyticsQuery = useAnalyticsSummary(windowDays);
  const transactionHistory = useTransactionHistory();

  function refreshMonitoringData() {
    analyticsQuery.reload();
    transactionHistory.historyQuery.reload();
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-lg font-semibold">Risk monitoring</h1>
        <div className="flex items-center gap-3">
          <AnalyticsWindowSelector windowDays={windowDays} onWindowChange={setWindowDays} />
          <button type="button" className="button-secondary" onClick={refreshMonitoringData}>
            Refresh
          </button>
        </div>
      </div>
      <AnalyticsOverview analyticsQuery={analyticsQuery} />
      <EvaluationHistory transactionHistory={transactionHistory} />
    </div>
  );
}
