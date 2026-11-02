import { useCallback } from "react";

import { useApiQuery } from "./useApiQuery.js";
import { fetchAnalyticsSummary } from "../services/analyticsService.js";

export function useAnalyticsSummary(windowDays) {
  const fetchSummary = useCallback(() => fetchAnalyticsSummary(windowDays), [windowDays]);
  return useApiQuery(fetchSummary);
}
