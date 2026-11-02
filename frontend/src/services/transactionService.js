import apiClient from "./apiClient.js";

/**
 * Submit a transaction for model-based risk evaluation.
 * The backend persists the assessment and returns its identifier.
 */
export async function evaluateTransaction(evaluationPayload) {
  const response = await apiClient.post("/transactions/evaluate", evaluationPayload);
  return response.data;
}

/**
 * Fetch one page of persisted evaluations, newest first.
 * Filters with empty values are omitted from the query string.
 */
export async function listTransactions({ page, pageSize, riskLabel, minRiskScore, maxRiskScore }) {
  const queryParameters = {
    page,
    page_size: pageSize,
    risk_label: riskLabel || undefined,
    min_risk_score: minRiskScore === "" ? undefined : minRiskScore,
    max_risk_score: maxRiskScore === "" ? undefined : maxRiskScore,
  };
  const response = await apiClient.get("/transactions/", { params: queryParameters });
  return response.data;
}

/** Fetch a single persisted evaluation by its record ID. */
export async function getTransaction(transactionId) {
  const response = await apiClient.get(`/transactions/${encodeURIComponent(transactionId)}`);
  return response.data;
}
