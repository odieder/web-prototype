const URGENCY_LABELS = {
  low: "Niedrig",
  medium: "Mittel",
  high: "Hoch",
};

export default function Result({ filename, category, summary, action, deadline, deadlineText, urgency }) {
  const urgencyClass = urgency ? `urgency-${urgency}` : "urgency-medium";
  return (
    <section className="result">
      <div className="result-header">
        <span className="badge">{category}</span>
        <span className={`urgency-chip ${urgencyClass}`}>Dringlichkeit: {URGENCY_LABELS[urgency] || "Mittel"}</span>
      </div>
      {filename && <p className="meta-line">Datei: {filename}</p>}

      <p className="result-label">Zusammenfassung</p>
      <p className="result-text">{summary}</p>

      <p className="result-label">Nächster Schritt</p>
      <p className="result-text">{action}</p>

      <p className="result-label">Frist</p>
      {deadline ? (
        <p className="deadline">
          {deadline}
          {deadlineText ? ` (${deadlineText})` : ""}
        </p>
      ) : (
        <p className="result-text">Keine Frist erkannt</p>
      )}
    </section>
  );
}
