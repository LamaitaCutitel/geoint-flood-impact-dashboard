# Sprint 4 — Cache Galați și Overpass

## Obiectiv
Asigură rulare rapidă și predictibilă pentru Galați.

## Modificări
- Prewarm și aplicația folosesc aceeași arie: `județ Galați + 1000 m`.
- Cache key OSM: `geometry_hash + category + query_version + limit`.
- Elimină ziua curentă din cache key; TTL-ul decide expirarea.
- Verifică existența reală a cache-ului înainte de mesajul `Cache Galați pregătit`.
- Status: valid, lipsă, incomplet, expirat.
- Timeout client HTTP: `75–90 s`.
- `prewarm_galati_cache.py`:
  - eșuează dacă există categorii incomplete;
  - salvează metadata;
  - afișează count, tile-uri, duplicate, relații și erori.

## Teste
- cache prewarm reutilizat;
- cache valid/expirat/incomplet;
- buffer 250 → 1000 fără redescărcare.
