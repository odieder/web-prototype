# 🚀 Dokunaut

## Projektzusammenfassung & aktueller Context

---

## 🎯 Produktidee

**Dokunaut** ist eine mobile/webbasierte Anwendung, die Nutzern hilft, **deutsche Behördenbriefe und Dokumente schnell zu verstehen und darauf zu reagieren**.

> 📸 *Foto hochladen → 🤖 Analyse → ✅ Klare To-dos*

**Claim:**
**„Dokunaut – Texte rein. To-dos raus.“**

---

## 🇩🇪 Fokus: Deutschland (Behördenbriefe)

Die App ist spezialisiert auf typische problematische Dokumente:

### 🧩 Top 5 Use Cases

* 📡 Rundfunk (GEZ / Beitragsservice)
* 🏥 Krankenkasse
* 💰 Finanzamt
* ⚠️ Mahnungen / Inkasso
* 🏠 Mietthemen

---

## 🧠 Kernfunktion (Pipeline)

1. Upload (Bild / PDF)
2. OCR (Texterkennung via Tesseract)
3. Klassifikation (LLM)
4. Zusammenfassung
5. Handlungsempfehlung
6. ⚠️ **Frist-Erkennung (USP)**

---

## 🔥 MVP Definition

### Input

* Foto oder PDF eines Dokuments

### Output (strukturierte JSON Antwort)

```json
{
  "category": "Finanzamt",
  "summary": "Du hast einen Steuerbescheid mit einer Nachzahlung erhalten.",
  "action": "Prüfe den Bescheid. Du kannst Einspruch einlegen.",
  "deadline": "2026-03-12",
  "deadline_text": "Du musst bis zum 12.03.2026 reagieren",
  "urgency": "high"
}
```

---

## 🧠 Kategorien

* Rundfunk
* Krankenkasse
* Finanzamt
* Mahnung
* Miete
* Sonstiges

---

## ⚠️ USP: Frist-Erkennung

Ziel:

> „Bis wann muss ich reagieren?“

### Umsetzung

* LLM-basierte Extraktion
* Optional: Regex-Fallback
* Unterstützt:

  * konkrete Daten („12.03.2026“)
  * relative Fristen („innerhalb von 14 Tagen“)

---

## 🏗️ Tech Stack

### Backend

* Python 3.12
* FastAPI
* Tesseract OCR (pytesseract)
* OpenAI API (LLM)

### Frontend

* React
* Upload UI (Drag & Drop)
* Anzeige:

  * Kategorie
  * Summary
  * Handlung
  * Frist
  * Dringlichkeit

### Dev Environment

* WSL2 (Ubuntu)
* Node.js / npm
* Docker (optional)
* VS Code

---

## 🔧 Backend Status

### ✅ Implementiert

* `/` Health Check
* `/upload` Endpoint
* OCR Verarbeitung
* Klassifikation via OpenAI
* Antwortgenerierung

### 🔜 Erweiterung

* Strukturierte JSON Outputs
* Frist-Erkennung
* Validierung & Parsing

---

## 💻 Frontend Status

### Features

* Upload (Image/PDF)
* Ladezustand
* Anzeige von:

  * Kategorie
  * Summary

### 🔜 Erweiterung

* App Rename → **Dokunaut**
* Zusatztext:

  > „Dokunaut – Texte rein. To-dos raus.“
* Anzeige:

  * Handlungsempfehlung
  * Frist (visuell hervorgehoben)
  * Dringlichkeit

---

## ☁️ Deployment Strategie

* MVP:

  * Railway / Render
* Empfehlung:

  * DigitalOcean
* Alternative:

  * IONOS (DSGVO)

---

## 🧠 Wichtige Learnings

* ChatGPT Plus ≠ API Zugriff
* API = Pay-as-you-go
* Multipart Upload kann tricky sein
* Swagger UI hilfreich
* WSL2 ideal für Dev

---

## 🚀 Aktueller Status

✅ Backend läuft
✅ OCR funktioniert
✅ Klassifikation implementiert
✅ Antwortgenerierung implementiert
🚧 Frontend in Entwicklung
🚧 Refactoring geplant

---

## 🔮 Nächste Schritte

* Frist-Erkennung implementieren
* Prompt verbessern (strukturierter Output)
* React UI erweitern
* Datenextraktion (Datum, Betrag)
* Authentifizierung
* Dokumentenspeicherung

---

## 💡 One-Liner

**Dokunaut verwandelt Behördenbriefe in klare To-dos.**
