import { useRef, useState } from "react";

const ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp", "image/tiff", "application/pdf"];

export default function Upload({ onUpload, isLoading }) {
  const inputRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);
  const [selectedName, setSelectedName] = useState("");
  const [localError, setLocalError] = useState("");

  const validateAndUpload = (file) => {
    if (!file) return;
    if (!ALLOWED_TYPES.includes(file.type)) {
      setLocalError("Bitte lade ein Bild oder PDF hoch.");
      return;
    }
    setLocalError("");
    setSelectedName(file.name);
    onUpload(file);
  };

  const onDrop = (event) => {
    event.preventDefault();
    setIsDragging(false);
    validateAndUpload(event.dataTransfer.files?.[0]);
  };

  const onInputChange = (event) => {
    validateAndUpload(event.target.files?.[0]);
  };

  return (
    <div
      className={`dropzone ${isDragging ? "dragging" : ""} ${isLoading ? "disabled" : ""}`}
      onDragOver={(e) => {
        e.preventDefault();
        setIsDragging(true);
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={onDrop}
    >
      <input
        ref={inputRef}
        type="file"
        accept="image/*,.pdf"
        onChange={onInputChange}
        disabled={isLoading}
        hidden
      />
      <p>Datei hierher ziehen oder</p>
      <button type="button" onClick={() => inputRef.current?.click()} disabled={isLoading}>
        Datei auswählen
      </button>
      <small>Unterstützt: JPG, PNG, WEBP, TIFF, PDF</small>
      {selectedName && <p className="filename">Ausgewählt: {selectedName}</p>}
      {localError && <p className="error">{localError}</p>}
    </div>
  );
}
