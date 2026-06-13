# Sprint 5 — QA final și CI

## Obiectiv
Pregătește demonstrația Galați.

## Modificări
- Adaugă GitHub Actions pentru:
  - instalare dependențe;
  - import curat;
  - `pytest`;
  - startup Streamlit smoke test.
- Adaugă test de integrare local:
  - prewarm Galați;
  - restart aplicație;
  - cache hit;
  - analiză rapidă;
  - analiză detaliată;
  - AOI;
  - buffer 1 / 250 / 1000;
  - thumbnail-uri;
  - comparator scene;
  - comparator rezultate;
  - Dynamic World;
  - OSM;
  - PDF.
- Salvează `.codex-sprint-logs/FINAL_QA.md`.

## Checklist manual
- fără layere duplicate;
- fără markeri dubli;
- fără mesaj verde fals;
- fără bara goală;
- fără thumbnail-uri lipsă neexplicate;
- OSM Galați din cache;
- PDF lizibil;
- timpi acceptabili.

## Final
Afișează:
- `git diff --stat`;
- `git status --short`;
- teste;
- probleme rămase.
Oprește-te înainte de commit și push.
