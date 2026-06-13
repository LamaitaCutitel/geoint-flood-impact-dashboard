# Technical Status

Data: 2026-06-13

## Stabil

- Entry point separat: `impact_tool.py`.
- Selectie explicita a scenelor individuale Sentinel-1 BEFORE si AFTER.
- Analiza SAR stricta AFTER minus BEFORE, procesata in Google Earth Engine.
- Crop la geometria judetului sau AOI-ului activ.
- Comparatie in aceeasi harta interactiva.
- Dynamic World optional, cu raportarea datelor efective disponibile.
- OSM incarcat dupa analiza SAR, cu cache persistent si sursa afisata in UI.
- Raport PDF generat local si salvat in `data/output/reports/`.
- Teste automate pentru stari, harta, OSM, Dynamic World si raport.

## Experimental

- `app.py` este dashboard-ul vechi, pastrat pentru explorare. Modurile sale mediane
  nu reprezinta metodologia principala a disertatiei.
- Calitatea rezultatului depinde de scene, praguri, geometria radar si datele
  auxiliare disponibile.

## Dependente externe

- Google Earth Engine necesita autentificare locala si acces la proiect.
- Dynamic World si tile-urile GEE necesita conexiune la internet.
- Overpass API este folosit numai cand cache-ul OSM local nu este disponibil.

## Date generate neversionate

- `cache/`
- `data/cache/`
- `data/output/`
- `.codex-sprint-logs/`
- `export_review/`
- rastere `.tif` si `.tiff`
