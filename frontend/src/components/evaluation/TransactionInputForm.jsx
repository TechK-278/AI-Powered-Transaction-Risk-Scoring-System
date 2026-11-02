import { useState } from "react";

import DatasetRowImport from "./DatasetRowImport.jsx";
import PcaComponentFields from "./PcaComponentFields.jsx";
import NumericField from "../shared/NumericField.jsx";
import {
  buildEvaluationPayload,
  createEmptyTransactionForm,
  validateTransactionForm,
} from "../../domain/transactionPayload.js";

export default function TransactionInputForm({ onSubmitEvaluation, isSubmitting }) {
  const [formValues, setFormValues] = useState(createEmptyTransactionForm);
  const [fieldErrors, setFieldErrors] = useState({});

  function updateField(fieldName, value) {
    setFormValues((previous) => ({ ...previous, [fieldName]: value }));
    setFieldErrors((previous) => ({ ...previous, [fieldName]: undefined }));
  }

  function applyImportedRow(importedValues) {
    setFormValues(importedValues);
    setFieldErrors({});
  }

  function resetForm() {
    setFormValues(createEmptyTransactionForm());
    setFieldErrors({});
  }

  function handleSubmit(event) {
    event.preventDefault();
    const validationErrors = validateTransactionForm(formValues);
    setFieldErrors(validationErrors);
    if (Object.keys(validationErrors).length === 0) {
      onSubmitEvaluation(buildEvaluationPayload(formValues));
    }
  }

  return (
    <form className="panel" onSubmit={handleSubmit} noValidate aria-labelledby="transaction-form-title">
      <div className="panel-header">
        <h2 id="transaction-form-title" className="panel-title">
          Transaction details
        </h2>
        <button type="button" className="button-secondary" onClick={resetForm}>
          Clear
        </button>
      </div>

      <div className="space-y-5 p-4">
        <div className="grid gap-4 sm:grid-cols-2">
          <NumericField
            name="amount"
            label="Amount (EUR)"
            value={formValues.amount}
            error={fieldErrors.amount}
            onValueChange={updateField}
          />
          <NumericField
            name="time"
            label="Time (seconds since first dataset transaction)"
            value={formValues.time}
            error={fieldErrors.time}
            onValueChange={updateField}
            hint="Used to derive the hour-of-day feature."
          />
        </div>

        <PcaComponentFields formValues={formValues} fieldErrors={fieldErrors} onValueChange={updateField} />

        <DatasetRowImport onRowImported={applyImportedRow} />
      </div>

      <div className="flex justify-end border-t border-line px-4 py-3">
        <button type="submit" className="button-primary" disabled={isSubmitting}>
          {isSubmitting ? "Evaluating…" : "Evaluate risk"}
        </button>
      </div>
    </form>
  );
}
