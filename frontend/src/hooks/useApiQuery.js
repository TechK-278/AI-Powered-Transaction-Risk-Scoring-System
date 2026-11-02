import { useCallback, useEffect, useRef, useState } from "react";

import { describeApiError } from "../services/apiErrorMessage.js";

/**
 * Runs a read-only API request whenever `fetchResource` changes identity
 * (callers wrap it in useCallback with its inputs as dependencies).
 * Responses from superseded requests are discarded so a slow earlier
 * request cannot overwrite newer results.
 */
export function useApiQuery(fetchResource) {
  const [queryState, setQueryState] = useState({ status: "loading", data: null, errorMessage: null });
  const latestRequestId = useRef(0);

  const runQuery = useCallback(async () => {
    const requestId = ++latestRequestId.current;
    setQueryState((previous) => ({ ...previous, status: "loading", errorMessage: null }));
    try {
      const data = await fetchResource();
      if (requestId === latestRequestId.current) {
        setQueryState({ status: "succeeded", data, errorMessage: null });
      }
    } catch (error) {
      if (requestId === latestRequestId.current) {
        setQueryState((previous) => ({ ...previous, status: "failed", errorMessage: describeApiError(error) }));
      }
    }
  }, [fetchResource]);

  useEffect(() => {
    runQuery();
  }, [runQuery]);

  return { ...queryState, reload: runQuery };
}
