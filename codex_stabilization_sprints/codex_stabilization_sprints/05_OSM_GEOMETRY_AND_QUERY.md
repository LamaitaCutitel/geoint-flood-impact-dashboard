# Sprint 5 — Geometrie și interogări OSM

## Obiectiv
Corectează completitudinea și intersecțiile OSM.

## Modificări
- Folosește Shapely pentru `intersects`, `intersection`, `distance`.
- Query pe AOI/județ + `1000 m`.
- Suport node, way, relation, multipolygon și găuri.
- Buildings: `way["building"]` și `relation["building"]`.
- Roads: include link-urile relevante.
- Recursive tiling la limită:
  - max depth;
  - deduplicare `(osm_type, osm_id)`;
  - warning dacă rămâne incomplet.
- Power:
  - rapid: substation, plant, generator, transformer;
  - detaliat: pole, tower, line, cable.

## Teste
- drum care traversează AOI;
- multipolygon;
- relation building;
- tiling recursiv;
- deduplicare;
- power rapid vs detaliat.
