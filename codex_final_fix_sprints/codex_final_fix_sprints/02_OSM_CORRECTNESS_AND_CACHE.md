# Sprint 2 — Corectitudine OSM și cache

## Obiectiv
Elimină duplicatele, stabilizează cache-ul și reduce încărcarea inutilă.

## Modificări
- Mută cache-ul la cale absolută:
  - `PROJECT_ROOT / "cache"`;
  - opțional `GEOINT_CACHE_DIR`.
- Asigură aceeași cale pentru aplicație și `prewarm_galati_cache.py`.
- După îmbinarea parserului legacy cu `_critical_layer()`:
  - deduplică feature-urile după `(osm_type, osm_id)`;
  - evită dublarea relație multipolygon / member ways.
- Păstrează raw OSM pe disc; în `state` păstrează doar:
  - status;
  - metrici;
  - subseturi afișabile;
  - referințe cache.
- Construiește index spațial Shapely `STRtree` pentru reclasificarea la schimbarea bufferului.
- Pentru drumuri și căi ferate păstrează separat:
  - `direct_geometry`;
  - `buffer_geometry`;
  - `context_geometry`.
- Harta:
  - direct = roșu;
  - buffer = portocaliu;
  - context = gri.
- Clădirile de referință:
  - sortează după distanță;
  - păstrează cele mai apropiate max. `750`.
- Preset Galați:
  - revine explicit la județ complet;
  - șterge AOI activ;
  - verifică snapshot/cache `Galați + 1000 m`.

## Teste
- fără markeri dubli;
- cache comun prewarm/aplicație;
- reluare aplicație = cache hit;
- separare direct/buffer/context;
- referințe sortate după distanță;
- preset Galați șterge AOI.
