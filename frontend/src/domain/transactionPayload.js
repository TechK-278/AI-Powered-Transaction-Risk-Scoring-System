/**
 * Form-state helpers for the transaction evaluation request.
 * Field names follow the backend TransactionEvaluationRequest schema:
 * `amount`, `time`, and the PCA components `v1` through `v28`.
 */

export const PCA_COMPONENT_KEYS = Array.from({ length: 28 }, (_, index) => `v${index + 1}`);

/** Column order of a row in the ULB credit card dataset (without the Class column). */
const DATASET_COLUMN_ORDER = ["time", ...PCA_COMPONENT_KEYS, "amount"];

export function createEmptyTransactionForm() {
  const pcaDefaults = Object.fromEntries(PCA_COMPONENT_KEYS.map((key) => [key, "0"]));
  return { amount: "", time: "0", ...pcaDefaults };
}

/**
 * Validate raw form values. Returns a map of field name to error message;
 * an empty map means the form can be submitted.
 */
export function validateTransactionForm(formValues) {
  const fieldErrors = {};
  const amount = Number(formValues.amount);
  const time = Number(formValues.time);

  if (formValues.amount.trim() === "" || !Number.isFinite(amount) || amount <= 0) {
    fieldErrors.amount = "Enter an amount greater than 0.";
  }
  if (formValues.time.trim() === "" || !Number.isFinite(time) || time < 0) {
    fieldErrors.time = "Enter elapsed seconds of 0 or more.";
  }
  for (const key of PCA_COMPONENT_KEYS) {
    if (formValues[key].trim() === "" || !Number.isFinite(Number(formValues[key]))) {
      fieldErrors[key] = "Enter a number.";
    }
  }
  return fieldErrors;
}

/** Convert validated form strings into the numeric request payload. */
export function buildEvaluationPayload(formValues) {
  return Object.fromEntries(
    DATASET_COLUMN_ORDER.map((key) => [key, Number(formValues[key])]),
  );
}

/**
 * Parse a comma-separated dataset row: Time, V1..V28, Amount, and an optional
 * trailing Class column which is ignored. Returns form values or throws an
 * Error describing why the row is unusable.
 */
export function parseDatasetRow(rowText) {
  const cells = rowText
    .trim()
    .split(",")
    .map((cell) => cell.trim().replace(/^"|"$/g, ""));

  const expectedLength = DATASET_COLUMN_ORDER.length;
  if (cells.length !== expectedLength && cells.length !== expectedLength + 1) {
    throw new Error(
      `Expected ${expectedLength} values (Time, V1–V28, Amount) but found ${cells.length}.`,
    );
  }

  const nonNumericIndex = cells
    .slice(0, expectedLength)
    .findIndex((cell) => cell === "" || !Number.isFinite(Number(cell)));
  if (nonNumericIndex !== -1) {
    throw new Error(`Value ${nonNumericIndex + 1} ("${cells[nonNumericIndex]}") is not a number.`);
  }

  return Object.fromEntries(DATASET_COLUMN_ORDER.map((key, index) => [key, cells[index]]));
}
