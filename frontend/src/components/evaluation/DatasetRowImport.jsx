import { useState } from "react";

import { parseDatasetRow } from "../../domain/transactionPayload.js";

/**
 * Lets an analyst paste one CSV row from the ULB credit card dataset
 * (Time, V1–V28, Amount[, Class]) instead of typing 30 values by hand.
 */
export default function DatasetRowImport({ onRowImported }) {
  const [rowText, setRowText] = useState("");
  const [parseError, setParseError] = useState(null);

  function applyDatasetRow() {
    try {
      onRowImported(parseDatasetRow(rowText));
      setParseError(null);
      setRowText("");
    } catch (error) {
      setParseError(error.message);
    }
  }

  return (
    <div className="space-y-2">
      <label htmlFor="dataset-row" className="field-label">
        Paste a dataset row (Time, V1–V28, Amount)
      </label>
      <textarea
        id="dataset-row"
        rows={2}
        className="field-input font-mono text-xs"
        value={rowText}
        aria-invalid={parseError ? "true" : "false"}
        aria-describedby={parseError ? "dataset-row-error" : undefined}
        onChange={(event) => setRowText(event.target.value)}
      />
      <div className="flex items-center gap-3">
        <button
          type="button"
          className="button-secondary"
          disabled={rowText.trim() === ""}
          onClick={applyDatasetRow}
        >
          Fill fields from row
        </button>
        {parseError && (
          <p id="dataset-row-error" className="text-xs text-risk-high">
            {parseError}
          </p>
        )}
      </div>
    </div>
  );
}
