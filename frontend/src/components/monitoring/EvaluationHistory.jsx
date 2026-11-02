import { useState } from "react";

import HistoryFilterBar from "./HistoryFilterBar.jsx";
import HistoryPagination from "./HistoryPagination.jsx";
import PredictionHistoryTable from "./PredictionHistoryTable.jsx";
import RecordLookupForm from "./RecordLookupForm.jsx";
import TransactionDetailPanel from "./TransactionDetailPanel.jsx";
import RequestErrorNotice from "../shared/RequestErrorNotice.jsx";

/** Filterable evaluation history alongside the selected record's details. */
export default function EvaluationHistory({ transactionHistory }) {
  const { historyQuery, appliedFilters, applyFilters, page, setPage } = transactionHistory;
  const [selectedTransaction, setSelectedTransaction] = useState(null);
  const historyPage = historyQuery.data;

  return (
    <div className="grid items-start gap-4 lg:grid-cols-3">
      <section className="panel lg:col-span-2" aria-labelledby="history-title" aria-busy={historyQuery.status === "loading"}>
        <div className="panel-header">
          <h2 id="history-title" className="panel-title">
            Evaluation history
          </h2>
        </div>
        <HistoryFilterBar appliedFilters={appliedFilters} onApplyFilters={applyFilters} />
        {historyQuery.status === "failed" && (
          <div className="p-4">
            <RequestErrorNotice message={historyQuery.errorMessage} />
          </div>
        )}
        {historyQuery.status !== "failed" && !historyPage && <p className="px-4 py-8 text-ink-muted">Loading history…</p>}
        {historyQuery.status !== "failed" && historyPage && (
          <>
            <PredictionHistoryTable
              transactions={historyPage.items}
              selectedTransactionId={selectedTransaction?.id}
              onSelectTransaction={setSelectedTransaction}
            />
            <HistoryPagination
              page={page}
              totalPages={historyPage.total_pages}
              totalRecords={historyPage.total}
              onPageChange={setPage}
            />
          </>
        )}
      </section>

      <div className="space-y-4 lg:sticky lg:top-4">
        <RecordLookupForm onRecordFound={setSelectedTransaction} />
        <TransactionDetailPanel transaction={selectedTransaction} />
      </div>
    </div>
  );
}
