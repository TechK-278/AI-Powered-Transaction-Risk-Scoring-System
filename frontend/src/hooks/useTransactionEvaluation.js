import { useCallback, useState } from "react";

import { describeApiError } from "../services/apiErrorMessage.js";
import { evaluateTransaction } from "../services/transactionService.js";

const INITIAL_EVALUATION_STATE = { status: "idle", assessment: null, errorMessage: null };

/**
 * Tracks the lifecycle of a single risk evaluation request:
 * idle → submitting → succeeded | failed.
 */
export function useTransactionEvaluation({ onEvaluated } = {}) {
  const [evaluationState, setEvaluationState] = useState(INITIAL_EVALUATION_STATE);

  const submitEvaluation = useCallback(
    async (evaluationPayload) => {
      setEvaluationState((previous) => ({ ...previous, status: "submitting", errorMessage: null }));
      try {
        const assessment = await evaluateTransaction(evaluationPayload);
        setEvaluationState({ status: "succeeded", assessment, errorMessage: null });
        onEvaluated?.(assessment);
      } catch (error) {
        setEvaluationState({
          status: "failed",
          assessment: null,
          errorMessage: describeApiError(error),
        });
      }
    },
    [onEvaluated],
  );

  return { evaluationState, submitEvaluation };
}
