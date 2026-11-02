const amountFormatter = new Intl.NumberFormat(undefined, {
  style: "currency",
  currency: "EUR",
  minimumFractionDigits: 2,
});

const timestampFormatter = new Intl.DateTimeFormat(undefined, {
  dateStyle: "medium",
  timeStyle: "medium",
});

/** Format a transaction amount. The training dataset is denominated in euros. */
export function formatTransactionAmount(amount) {
  return amountFormatter.format(amount);
}

/** Format a probability in [0, 1] as a percentage with two decimals. */
export function formatFraudProbability(probability) {
  return `${(probability * 100).toFixed(2)}%`;
}

export function formatTimestamp(isoTimestamp) {
  return timestampFormatter.format(new Date(isoTimestamp));
}

/** Format dataset elapsed seconds (the `Time` feature) as e.g. "1d 02:15:30". */
export function formatElapsedSeconds(totalSeconds) {
  const wholeSeconds = Math.floor(totalSeconds);
  const days = Math.floor(wholeSeconds / 86400);
  const clock = new Date((wholeSeconds % 86400) * 1000).toISOString().slice(11, 19);
  return days > 0 ? `${days}d ${clock}` : clock;
}

export function shortenIdentifier(identifier) {
  return identifier.slice(0, 8);
}
