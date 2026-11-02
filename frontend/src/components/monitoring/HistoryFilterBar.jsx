import { useState } from "react";

import { RISK_LABELS } from "../../domain/riskTiers.js";
import { EMPTY_HISTORY_FILTERS } from "../../hooks/useTransactionHistory.js";

function parseScoreBound(rawValue) {
  if (rawValue.trim() === "") {
    return { value: "", valid: true };
  }
  const score = Number(rawValue);
  return { value: score, valid: Number.isInteger(score) && score >= 0 && score <= 100 };
}

/** Draft filters are only sent to the API when the analyst applies them. */
export default function HistoryFilterBar({ appliedFilters, onApplyFilters }) {
  const [draftFilters, setDraftFilters] = useState({
    riskLabel: appliedFilters.riskLabel,
    minRiskScore: String(appliedFilters.minRiskScore),
    maxRiskScore: String(appliedFilters.maxRiskScore),
  });
  const [filterError, setFilterError] = useState(null);

  function updateDraft(fieldName, value) {
    setDraftFilters((previous) => ({ ...previous, [fieldName]: value }));
  }

  function handleSubmit(event) {
    event.preventDefault();
    const minimum = parseScoreBound(draftFilters.minRiskScore);
    const maximum = parseScoreBound(draftFilters.maxRiskScore);
    if (!minimum.valid || !maximum.valid) {
      setFilterError("Score bounds must be whole numbers from 0 to 100.");
      return;
    }
    if (minimum.value !== "" && maximum.value !== "" && minimum.value > maximum.value) {
      setFilterError("Minimum score cannot exceed maximum score.");
      return;
    }
    setFilterError(null);
    onApplyFilters({ riskLabel: draftFilters.riskLabel, minRiskScore: minimum.value, maxRiskScore: maximum.value });
  }

  function resetFilters() {
    setDraftFilters({ riskLabel: "", minRiskScore: "", maxRiskScore: "" });
    setFilterError(null);
    onApplyFilters(EMPTY_HISTORY_FILTERS);
  }

  return (
    <form className="flex flex-wrap items-end gap-3 border-b border-line px-4 py-3" onSubmit={handleSubmit} aria-label="Filter evaluations">
      <div>
        <label htmlFor="filter-tier" className="field-label">
          Tier
        </label>
        <select
          id="filter-tier"
          className="field-input w-32"
          value={draftFilters.riskLabel}
          onChange={(event) => updateDraft("riskLabel", event.target.value)}
        >
          <option value="">All tiers</option>
          {RISK_LABELS.map((label) => (
            <option key={label} value={label}>
              {label}
            </option>
          ))}
        </select>
      </div>
      <div>
        <label htmlFor="filter-min-score" className="field-label">
          Min score
        </label>
        <input
          id="filter-min-score"
          className="field-input w-24"
          inputMode="numeric"
          value={draftFilters.minRiskScore}
          onChange={(event) => updateDraft("minRiskScore", event.target.value)}
        />
      </div>
      <div>
        <label htmlFor="filter-max-score" className="field-label">
          Max score
        </label>
        <input
          id="filter-max-score"
          className="field-input w-24"
          inputMode="numeric"
          value={draftFilters.maxRiskScore}
          onChange={(event) => updateDraft("maxRiskScore", event.target.value)}
        />
      </div>
      <button type="submit" className="button-primary">
        Apply
      </button>
      <button type="button" className="button-secondary" onClick={resetFilters}>
        Reset
      </button>
      {filterError && (
        <p role="alert" className="w-full text-xs text-risk-high-ink">
          {filterError}
        </p>
      )}
    </form>
  );
}
