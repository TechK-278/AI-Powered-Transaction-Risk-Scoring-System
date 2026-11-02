import RiskLabelBadge from "../shared/RiskLabelBadge.jsx";
import {
  formatFraudProbability,
  formatTimestamp,
  formatTransactionAmount,
  shortenIdentifier,
} from "../../domain/displayFormatters.js";

const HEADER_CELL = "px-4 py-2 text-left text-xs font-medium text-ink-muted";
const NUMERIC_HEADER_CELL = "px-4 py-2 text-right text-xs font-medium text-ink-muted";

/** Persisted evaluations, newest first. Selecting a record opens it in the detail panel. */
export default function PredictionHistoryTable({ transactions, selectedTransactionId, onSelectTransaction }) {
  if (transactions.length === 0) {
    return <p className="px-4 py-8 text-center text-ink-muted">No evaluations match the current filters.</p>;
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse">
        <caption className="sr-only">Transaction risk evaluations</caption>
        <thead className="border-b border-line bg-canvas">
          <tr>
            <th scope="col" className={HEADER_CELL}>Evaluated</th>
            <th scope="col" className={HEADER_CELL}>Record</th>
            <th scope="col" className={NUMERIC_HEADER_CELL}>Amount</th>
            <th scope="col" className={NUMERIC_HEADER_CELL}>Probability</th>
            <th scope="col" className={NUMERIC_HEADER_CELL}>Score</th>
            <th scope="col" className={HEADER_CELL}>Tier</th>
          </tr>
        </thead>
        <tbody>
          {transactions.map((transaction) => {
            const isSelected = transaction.id === selectedTransactionId;
            return (
              <tr
                key={transaction.id}
                className={`border-b border-line last:border-b-0 ${isSelected ? "bg-accent-soft" : "hover:bg-canvas"}`}
              >
                <td className="whitespace-nowrap px-4 py-2">{formatTimestamp(transaction.created_at)}</td>
                <td className="px-4 py-2">
                  <button
                    type="button"
                    className="numeric text-accent underline-offset-2 hover:underline"
                    aria-pressed={isSelected}
                    aria-label={`Show details for record ${transaction.id}`}
                    onClick={() => onSelectTransaction(transaction)}
                  >
                    {shortenIdentifier(transaction.id)}
                  </button>
                </td>
                <td className="numeric px-4 py-2 text-right">{formatTransactionAmount(transaction.amount)}</td>
                <td className="numeric px-4 py-2 text-right">{formatFraudProbability(transaction.fraud_probability)}</td>
                <td className="numeric px-4 py-2 text-right font-semibold">{transaction.risk_score}</td>
                <td className="px-4 py-2">
                  <RiskLabelBadge riskLabel={transaction.risk_label} />
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
