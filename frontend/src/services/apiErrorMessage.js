/**
 * Convert an Axios error into a message an analyst can act on.
 * FastAPI returns `detail` as a string for handled errors and as a list of
 * field errors for request validation failures (HTTP 422).
 */
export function describeApiError(error) {
  if (!error.response) {
    return "The risk service could not be reached. Check that the backend is running.";
  }

  const { status, data } = error.response;
  const detail = data?.detail;

  if (Array.isArray(detail)) {
    const fieldMessages = detail.map((issue) => {
      const fieldName = issue.loc?.slice(1).join(".") || "request";
      return `${fieldName}: ${issue.msg}`;
    });
    return `The request was rejected. ${fieldMessages.join("; ")}`;
  }

  if (typeof detail === "string" && detail.length > 0) {
    return detail;
  }

  return `The risk service returned an unexpected response (HTTP ${status}).`;
}
