# Sprint 1 — Status SAR și invalidarea rezultatelor vechi

## Obiectiv
Elimină riscul afișării unor rezultate vechi sau a unor valori `0` false.

## Probleme
- Parametrii SAR se modifică în sidebar fără invalidarea rezultatului anterior.
- Erorile de calcul al suprafeței pot deveni `0.0`.
- Erorile de vectorizare pot deveni `None`.
- Erorile de tile pot rămâne fără diagnostic clar.

## Modificări
- Creează `update_sar_parameters(state, ...)`.
- La schimbarea pragului, smoothing-ului, minimum connected pixels sau scale:
  - invalidează SAR, OSM, Dynamic World și PDF;
  - dezactivează comparatoarele tematice;
  - afișează mesajul `Parametrii SAR s-au schimbat. Rulează din nou analiza.`
- Înlocuiește rezultatele silențioase cu obiecte:
  - `{status, value, error}`;
  - `{status, geometry, error, duration_seconds}`;
  - `{status, url, error}`.
- În UI nu afișa `0 km²` dacă statusul este eroare sau indisponibil.
- Afișează separat:
  - raster SAR disponibil;
  - metrici disponibile;
  - vectorizare disponibilă;
  - impact OSM disponibil.

## Teste
- schimbare parametri invalidează analiza și PDF-ul;
- eroare metrică != zero real;
- vectorizare eșuată produce mesaj;
- tile lipsă produce diagnostic UI.
