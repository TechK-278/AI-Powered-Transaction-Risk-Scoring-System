import { useState } from "react";

import { describeApiError } from "../../services/apiErrorMessage.js";
import { getTransaction } from "../../services/transactionService.js";

const UUID_PATTERN = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

/** Look up a single evaluation by its full record ID. */
export default function RecordLookupForm({ onRecordFound }) {
  const [recordId, setRecordId] = useState("");
  const [lookupError, setLookupError] = useState(null);
  const [isSearching, setIsSearching] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    const trimmedId = recordId.trim();
    if (!UUID_PATTERN.test(trimmedId)) {
      setLookupError("Enter a full record ID (36-character UUID).");
      return;
    }
    setIsSearching(true);
    setLookupError(null);
    try {
      onRecordFound(await getTransaction(trimmedId));
    } catch (error) {
      setLookupError(describeApiError(error));
    } finally {
      setIsSearching(false);
    }
  }

  return (
    <form className="panel p-4" onSubmit={handleSubmit} aria-label="Find evaluation by record ID">
      <label htmlFor="record-lookup" className="field-label">
        Find by record ID
      </label>
      <div className="flex gap-2">
        <input
          id="record-lookup"
          className="field-input font-mono text-xs"
          value={recordId}
          autoComplete="off"
          spellCheck="false"
          aria-invalid={lookupError ? "true" : "false"}
          aria-describedby={lookupError ? "record-lookup-error" : undefined}
          onChange={(event) => setRecordId(event.target.value)}
        />
        <button type="submit" className="button-secondary" disabled={isSearching}>
          {isSearching ? "Finding…" : "Find"}
        </button>
      </div>
      {lookupError && (
        <p id="record-lookup-error" className="mt-1 text-xs text-risk-high-ink">
          {lookupError}
        </p>
      )}
    </form>
  );
}
