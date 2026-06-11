# Sprint 6 — Impact operațional OSM

## Precondiție

Rulează numai după stabilizarea rasterului.

## Obiectiv

Adaugă:
1. clădiri;
2. drumuri;
3. obiective critice;
4. căi ferate;
5. poduri.

## Performanță

- bbox flood extent;
- buffer configurabil;
- cache;
- query limitat;
- evită vectorizarea completă la rezoluție maximă în preview.

## Indicatori

- clădiri potențial afectate;
- km drum intersectați;
- obiective critice;
- km cale ferată;
- poduri.

## Formulare

Folosește:
- `potențial afectat`;
- `intersectat`;
- `expunere estimată`.

## Restricții

- fără EMS;
- fără scor general 0–100.

## La final

- rulează `pytest`;
- verifică vizual;
- afișează `git diff --stat`;
- rulează `/review`;
- oprește-te înainte de commit.
