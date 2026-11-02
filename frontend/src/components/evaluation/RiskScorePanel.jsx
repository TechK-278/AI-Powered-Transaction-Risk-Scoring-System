import RiskScoreScale from "./RiskScoreScale.jsx";
import RequestErrorNotice from "../shared/RequestErrorNotice.jsx";
import RiskLabelBadge from "../shared/RiskLabelBadge.jsx";
import { findRiskTier } from "../../domain/riskTiers.js";
import { formatFraudProbability, formatTimestamp } from "../../domain/displayFormatters.js";

function AssessmentDetails({ assessment }) {
  const tier = findRiskTier(assessment.risk_label);

  return (
    <div className="space-y-4">
      <div className="flex items-end justify-between gap-4">
        <div>
          <p className="text-xs text-ink-muted">Risk score</p>
          <p className="numeric text-4xl font-semibold leading-none">{assessment.risk_score}</p>
        </div>
        <div className="text-right">
          <RiskLabelBadge riskLabel={assessment.risk_label} />
          {tier && <p className="mt-1 text-xs text-ink-muted">{tier.summary}</p>}
        </div>
      </div>

      <RiskScoreScale riskScore={assessment.risk_score} />

      <dl className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-1.5 border-t border-line pt-3">
        <dt className="text-ink-muted">Fraud probability</dt>
        <dd className="numeric text-right">{formatFraudProbability(assessment.fraud_probability)}</dd>
        {assessment.created_at && (
          <>
            <dt className="text-ink-muted">Evaluated</dt>
            <dd className="text-right">{formatTimestamp(assessment.created_at)}</dd>
          </>
        )}
        {assessment.id && (
          <>
            <dt className="text-ink-muted">Record ID</dt>
            <dd className="numeric truncate text-right text-xs" title={assessment.id}>
              {assessment.id}
            </dd>
          </>
        )}
      </dl>
    </div>
  );
}

/** Shows the outcome of the most recent evaluation request. */
export default function RiskScorePanel({ evaluationState }) {
  const { status, assessment, errorMessage } = evaluationState;

  return (
    <section className="panel" aria-labelledby="risk-panel-title" aria-live="polite" aria-busy={status === "submitting"}>
      <div className="panel-header">
        <h2 id="risk-panel-title" className="panel-title">
          Risk assessment
        </h2>
      </div>
      <div className="p-4">
        {status === "idle" && (
          <p className="text-ink-muted">Submit a transaction to see its modeled fraud risk.</p>
        )}
        {status === "submitting" && !assessment && <p className="text-ink-muted">Scoring transaction…</p>}
        {status === "failed" && <RequestErrorNotice message={errorMessage} />}
        {assessment && status !== "failed" && <AssessmentDetails assessment={assessment} />}
      </div>
      <p className="border-t border-line px-4 py-2 text-xs text-ink-muted">
        Scores describe statistical model output only; they are not an automated decision.
      </p>
    </section>
  );
}
