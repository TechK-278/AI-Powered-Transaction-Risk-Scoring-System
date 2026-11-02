import { useCallback, useState } from "react";

import { useApiQuery } from "./useApiQuery.js";
import { listTransactions } from "../services/transactionService.js";

export const HISTORY_PAGE_SIZE = 20;
export const EMPTY_HISTORY_FILTERS = { riskLabel: "", minRiskScore: "", maxRiskScore: "" };

/** Paginated, filterable view over persisted evaluations. */
export function useTransactionHistory() {
  const [appliedFilters, setAppliedFilters] = useState(EMPTY_HISTORY_FILTERS);
  const [page, setPage] = useState(1);

  const fetchHistoryPage = useCallback(
    () => listTransactions({ page, pageSize: HISTORY_PAGE_SIZE, ...appliedFilters }),
    [page, appliedFilters],
  );
  const historyQuery = useApiQuery(fetchHistoryPage);

  const applyFilters = useCallback((nextFilters) => {
    setAppliedFilters(nextFilters);
    setPage(1);
  }, []);

  return { historyQuery, appliedFilters, applyFilters, page, setPage };
}
