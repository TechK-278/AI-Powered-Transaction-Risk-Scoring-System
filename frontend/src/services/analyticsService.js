import apiClient from "./apiClient.js";

/** Fetch aggregate risk analytics with per-day volume for the last `windowDays` days. */
export async function fetchAnalyticsSummary(windowDays) {
  const response = await apiClient.get("/analytics/summary", { params: { window_days: windowDays } });
  return response.data;
}
