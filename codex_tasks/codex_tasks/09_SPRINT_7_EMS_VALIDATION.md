# Sprint 7 — Validare Copernicus EMS

## Precondiție

Rulează după stabilizare și OSM.

## Input

Upload:
```text
GeoJSON
GPKG
Shapefile ZIP
```

## Calcule

- suprafață SAR;
- suprafață EMS;
- intersecție;
- uniune;
- IoU;
- precision;
- recall;
- F1;
- false positive area;
- false negative area.

## Layere

- SAR;
- EMS;
- intersecție;
- false positives;
- false negatives.

## Formulare

Nu folosi `adevăr absolut`.
Folosește `produs operațional de referință`.

## La final

- rulează `pytest`;
- verifică vizual;
- afișează `git diff --stat`;
- rulează `/review`;
- oprește-te înainte de commit.
