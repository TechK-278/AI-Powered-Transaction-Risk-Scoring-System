import apiClient from "./apiClient.js";

/**
 * Submit a transaction for model-based risk evaluation.
 * The backend persists the assessment and returns its identifier.
 */
export async function evaluateTransaction(evaluationPayload) {
  const response = await apiClient.post("/transactions/evaluate", evaluationPayload);
  return response.data;
}
