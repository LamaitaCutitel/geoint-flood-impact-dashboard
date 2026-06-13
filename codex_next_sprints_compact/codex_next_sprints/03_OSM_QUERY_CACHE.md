# Sprint 3 — OSM query și cache

## Obiectiv
Încarcă mai multe date fără trunchiere silențioasă.

## Modificări
- Limite:
  - buildings `50000`
  - roads `25000`
  - railways `10000`
  - bridges `10000`
  - critical `15000`
- Timeout Overpass `60 s`.
- Detectează atingerea limitei.
- Dacă limita este atinsă: împarte bbox în 4, reinteroghează, deduplică după `(osm_type, osm_id)`.
- Cache persistent per categorie și tile.
- Script `scripts/prewarm_galati_cache.py`.
- Afișează sursă, dată cache și completitudine.

## Teste
Limite, tiling, deduplicare, warning, prewarm Galați.
