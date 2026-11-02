export default function RequestErrorNotice({ message }) {
  if (!message) {
    return null;
  }

  return (
    <div role="alert" className="rounded border border-risk-high/40 bg-risk-high-soft px-3 py-2 text-risk-high-ink">
      {message}
    </div>
  );
}
