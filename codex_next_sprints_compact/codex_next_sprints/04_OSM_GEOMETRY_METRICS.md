# Sprint 4 — Geometrie și metrici OSM

## Obiectiv
Corectează intersecțiile și statisticile.

## Modificări
- Shapely pentru `intersects`, `intersection`, `distance`.
- Suport `node`, `way`, `relation`, multipolygon și găuri.
- Query pe aria activă extinsă cu bufferul analitic.
- Păstrează geometria originală și decupată.
- Drumuri/căi ferate: lungime efectiv intersectată și lungime în buffer.
- Clădiri: număr direct/buffer, suprafață totală, suprapunere efectivă, complet/parțial.
- Status pentru obiecte din exteriorul AOI, dar în buffer.

## Teste
Traversare AOI, multipolygon, lungimi parțiale, suprafețe parțiale, exterior AOI în buffer.
