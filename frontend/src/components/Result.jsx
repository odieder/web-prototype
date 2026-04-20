export default function Result({ category, response }) {
  return (
    <section className="result">
      <div className="result-header">
        <span className="badge">{category}</span>
      </div>
      <p>{response}</p>
    </section>
  );
}
