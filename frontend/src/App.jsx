import { useState } from "react";
import Upload from "./components/Upload";
import Result from "./components/Result";

const API_URL = "http://127.0.0.1:8000/upload";

export default function App() {
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const handleUpload = async (file) => {
    setIsLoading(true);
    setError("");
    setResult(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        body: formData,
      });

      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        throw new Error(data?.detail || "Upload fehlgeschlagen.");
      }
      setResult({
        filename: data.filename,
        category: data.category,
        summary: data.summary,
        action: data.action,
        deadline: data.deadline,
        deadlineText: data.deadline_text,
        urgency: data.urgency,
      });
    } catch (err) {
      if (err instanceof TypeError) {
        setError(
          "Verbindung zum Backend fehlgeschlagen. Bitte prüfe, ob FastAPI auf http://127.0.0.1:8000 läuft und CORS aktiviert ist."
        );
      } else {
        setError(err.message || "Beim Upload ist ein Fehler aufgetreten.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <header className="topbar">
        <div className="topbar-inner">Dokunaut – Texte rein. To-Dos raus.</div>
      </header>

      <main className="page">
        <section className="card">
          <h1>Dokument-Analyse</h1>
          <p className="subtitle">Lade ein Bild oder PDF hoch und erhalte eine kurze Einschätzung.</p>

          <Upload onUpload={handleUpload} isLoading={isLoading} />

          {isLoading && <p className="status">Datei wird verarbeitet...</p>}
          {error && <p className="error">{error}</p>}
          {result && (
            <Result
              filename={result.filename}
              category={result.category}
              summary={result.summary}
              action={result.action}
              deadline={result.deadline}
              deadlineText={result.deadlineText}
              urgency={result.urgency}
            />
          )}
        </section>
      </main>
    </>
  );
}
