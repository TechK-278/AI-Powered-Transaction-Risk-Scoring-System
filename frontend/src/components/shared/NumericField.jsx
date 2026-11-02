/**
 * Labelled numeric text input with inline validation message.
 * Values are kept as strings so partially typed numbers (e.g. "-") are not lost.
 */
export default function NumericField({ name, label, value, error, onValueChange, hint, compact = false }) {
  const inputId = `field-${name}`;
  const messageId = `${inputId}-message`;

  return (
    <div>
      <label htmlFor={inputId} className={compact ? "field-label font-mono" : "field-label"}>
        {label}
      </label>
      <input
        id={inputId}
        name={name}
        type="text"
        inputMode="decimal"
        autoComplete="off"
        className="field-input"
        value={value}
        aria-invalid={error ? "true" : "false"}
        aria-describedby={error || hint ? messageId : undefined}
        onChange={(event) => onValueChange(name, event.target.value)}
      />
      {error ? (
        <p id={messageId} className="mt-1 text-xs text-risk-high-ink">
          {error}
        </p>
      ) : (
        hint && (
          <p id={messageId} className="mt-1 text-xs text-ink-muted">
            {hint}
          </p>
        )
      )}
    </div>
  );
}
