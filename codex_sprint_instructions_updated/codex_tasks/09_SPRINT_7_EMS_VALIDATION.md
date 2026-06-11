# Sprint 7 — Validare Copernicus EMS

## Precondiție

Nu începe înainte de stabilizarea rasterului și a modulului OSM.

## Obiectiv

Adaugă validare externă față de un produs de referință Copernicus EMS.

## Input

Permite upload:

```text
GeoJSON
GPKG
Shapefile ZIP
```

cu extensia de referință EMS.

## Calcule

- suprafață SAR;
- suprafață EMS;
- intersecție;
- uniune;
- IoU;
- precision;
- recall;
- F1-score;
- false positive area;
- false negative area.

## Layere

- extindere SAR;
- extindere EMS;
- intersecție;
- false positives;
- false negatives.

## UI

În tab-ul `Validare`:

- upload;
- status fișier;
- metric cards;
- explicații metodologice;
- hartă;
- export.

## Raport

Adaugă:

- sursa EMS;
- data produsului;
- fișier încărcat;
- metrici;
- limitări;
- diferențe temporale dintre achiziția SAR și produsul EMS.

## Restricții

- nu numi produsul EMS `adevăr absolut`;
- folosește formularea `produs operațional de referință`.

## Teste

Adaugă teste pentru:

- upload valid;
- upload invalid;
- geometrie goală;
- IoU;
- precision;
- recall;
- F1;
- false positives;
- false negatives.

## La final

- rulează `pytest`;
- verifică vizual;
- afișează `git diff --stat`;
- rulează `/review`;
- nu face push;
- oprește-te.
