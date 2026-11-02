import NumericField from "../shared/NumericField.jsx";
import { PCA_COMPONENT_KEYS } from "../../domain/transactionPayload.js";

/**
 * Collapsible grid of the 28 anonymised PCA features (V1–V28).
 * Opens automatically when any component has a validation error.
 */
export default function PcaComponentFields({ formValues, fieldErrors, onValueChange }) {
  const nonZeroCount = PCA_COMPONENT_KEYS.filter((key) => Number(formValues[key]) !== 0).length;
  const hasErrors = PCA_COMPONENT_KEYS.some((key) => fieldErrors[key]);

  return (
    <details className="rounded border border-line" open={hasErrors || undefined}>
      <summary className="cursor-pointer select-none px-3 py-2 text-sm font-medium">
        PCA components V1–V28
        <span className="ml-2 font-normal text-ink-muted">{nonZeroCount} of 28 non-zero</span>
      </summary>
      <fieldset className="grid grid-cols-2 gap-3 border-t border-line p-3 sm:grid-cols-4 lg:grid-cols-7">
        <legend className="sr-only">PCA components V1 to V28</legend>
        {PCA_COMPONENT_KEYS.map((key) => (
          <NumericField
            key={key}
            name={key}
            label={key.toUpperCase()}
            value={formValues[key]}
            error={fieldErrors[key]}
            onValueChange={onValueChange}
            compact
          />
        ))}
      </fieldset>
    </details>
  );
}
