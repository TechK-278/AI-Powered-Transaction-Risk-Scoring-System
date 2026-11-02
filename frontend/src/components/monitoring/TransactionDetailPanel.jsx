import RiskLabelBadge from "../shared/RiskLabelBadge.jsx";
import { findRiskTier } from "../../domain/riskTiers.js";
import {
  formatElapsedSeconds,
  formatFraudProbability,
  formatTimestamp,
  formatTransactionAmount,
} from "../../domain/displayFormatters.js";

function DetailRow({ term, children, numeric = false }) {
  return (
    <>
      <dt className="text-ink-muted">{term}</dt>
      <dd className={numeric ? "numeric text-right" : "text-right"}>{children}</dd>
    </>
  );
}

/** Full record of one persisted evaluation. */
export default function TransactionDetailPanel({ transaction }) {
  return (
    <section className="panel" aria-labelledby="detail-title" aria-live="polite">
      <div className="panel-header">
        <h2 id="detail-title" className="panel-title">
          Evaluation record
        </h2>
        {transaction && <RiskLabelBadge riskLabel={transaction.risk_label} />}
      </div>
      {transaction ? (
        <div className="space-y-3 p-4">
          <p className="numeric break-all text-xs text-ink-muted">{transaction.id}</p>
          <dl className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-1.5">
            <DetailRow term="Risk score" numeric>
              {transaction.risk_score}
            </DetailRow>
            <DetailRow term="Tier meaning">{findRiskTier(transaction.risk_label)?.summary ?? "—"}</DetailRow>
            <DetailRow term="Fraud probability" numeric>
              {formatFraudProbability(transaction.fraud_probability)}
            </DetailRow>
            <DetailRow term="Amount" numeric>
              {formatTransactionAmount(transaction.amount)}
            </DetailRow>
            <DetailRow term="Dataset time" numeric>
              {formatElapsedSeconds(transaction.time)}
            </DetailRow>
            <DetailRow term="Evaluated">{formatTimestamp(transaction.created_at)}</DetailRow>
          </dl>
        </div>
      ) : (
        <p className="p-4 text-ink-muted">Select a record in the table or look one up by ID.</p>
      )}
    </section>
  );
}
