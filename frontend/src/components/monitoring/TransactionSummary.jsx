import { findRiskTier } from "../../domain/riskTiers.js";
import { formatFraudProbability } from "../../domain/displayFormatters.js";

function formatShare(count, total) {
  return total === 0 ? "0%" : `${((count / total) * 100).toFixed(1)}%`;
}

function RiskTierMixBar({ riskLabelCounts, total }) {
  if (total === 0) {
    return <div className="h-2 rounded-sm bg-canvas" />;
  }
  return (
    <div className="flex h-2 gap-0.5" aria-hidden="true">
      {riskLabelCounts
        .filter((item) => item.count > 0)
        .map((item) => (
          <div
            key={item.risk_label}
            className="rounded-sm"
            style={{ flexGrow: item.count, backgroundColor: findRiskTier(item.risk_label)?.markColor }}
          />
        ))}
    </div>
  );
}

/** Headline figures across every persisted evaluation. */
export default function TransactionSummary({ summary }) {
  const total = summary.total_evaluations;

  return (
    <section className="panel grid gap-px overflow-hidden bg-line sm:grid-cols-2 lg:grid-cols-4" aria-label="Evaluation summary">
      <div className="bg-surface p-4">
        <p className="text-xs text-ink-muted">Evaluations recorded</p>
        <p className="numeric mt-1 text-2xl font-semibold">{total.toLocaleString()}</p>
      </div>
      <div className="bg-surface p-4">
        <p className="text-xs text-ink-muted">Mean risk score</p>
        <p className="numeric mt-1 text-2xl font-semibold">
          {summary.average_risk_score === null ? "—" : summary.average_risk_score.toFixed(1)}
        </p>
      </div>
      <div className="bg-surface p-4">
        <p className="text-xs text-ink-muted">Mean fraud probability</p>
        <p className="numeric mt-1 text-2xl font-semibold">
          {summary.average_fraud_probability === null ? "—" : formatFraudProbability(summary.average_fraud_probability)}
        </p>
      </div>
      <div className="bg-surface p-4">
        <p className="mb-2 text-xs text-ink-muted">Tier mix</p>
        <RiskTierMixBar riskLabelCounts={summary.risk_label_counts} total={total} />
        <dl className="mt-2 grid grid-cols-3 gap-2 text-xs">
          {summary.risk_label_counts.map((item) => (
            <div key={item.risk_label}>
              <dt className="flex items-center gap-1.5 text-ink-muted">
                <span
                  className="inline-block size-2 rounded-sm"
                  style={{ backgroundColor: findRiskTier(item.risk_label)?.markColor }}
                  aria-hidden="true"
                />
                {item.risk_label}
              </dt>
              <dd className="numeric text-ink">
                {item.count.toLocaleString()} · {formatShare(item.count, total)}
              </dd>
            </div>
          ))}
        </dl>
      </div>
    </section>
  );
}
