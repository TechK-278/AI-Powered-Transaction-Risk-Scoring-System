import RiskScorePanel from "../components/evaluation/RiskScorePanel.jsx";
import TransactionInputForm from "../components/evaluation/TransactionInputForm.jsx";
import { useTransactionEvaluation } from "../hooks/useTransactionEvaluation.js";

/** Score a single transaction and review the resulting assessment. */
export default function EvaluationPage() {
  const { evaluationState, submitEvaluation } = useTransactionEvaluation();

  return (
    <div className="grid items-start gap-4 lg:grid-cols-3">
      <div className="lg:col-span-2">
        <TransactionInputForm
          onSubmitEvaluation={submitEvaluation}
          isSubmitting={evaluationState.status === "submitting"}
        />
      </div>
      <div className="lg:sticky lg:top-4">
        <RiskScorePanel evaluationState={evaluationState} />
      </div>
    </div>
  );
}
