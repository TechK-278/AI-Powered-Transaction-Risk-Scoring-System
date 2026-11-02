export default function HistoryPagination({ page, totalPages, totalRecords, onPageChange }) {
  const lastPage = Math.max(totalPages, 1);

  return (
    <nav className="flex items-center justify-between gap-4 border-t border-line px-4 py-2" aria-label="History pages">
      <p className="text-xs text-ink-muted">
        {totalRecords.toLocaleString()} matching · page {page} of {lastPage}
      </p>
      <div className="flex gap-2">
        <button type="button" className="button-secondary" disabled={page <= 1} onClick={() => onPageChange(page - 1)}>
          Previous
        </button>
        <button type="button" className="button-secondary" disabled={page >= lastPage} onClick={() => onPageChange(page + 1)}>
          Next
        </button>
      </div>
    </nav>
  );
}
