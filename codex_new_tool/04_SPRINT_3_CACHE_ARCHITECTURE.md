# Sprint 3 — Arhitectura de cache

## Obiectiv

Implementează cache persistent și invalidare selectivă.

## Tipuri de cache

### 1. Limite administrative
Păstrează:
- geometrii județe;
- bbox;
- centroizi.

### 2. Scene Sentinel-1
Cheie:
```text
AOI_hash
interval temporal
polarizare
orbit_pass
```

Păstrează:
- scene;
- metadate;
- thumbnails;
- acoperire AOI.

### 3. Tile URL-uri GEE
Cheie:
```text
AOI_hash
scene_before_id
scene_after_id
layer_id
parametri
```

### 4. Dynamic World
Cheie:
```text
AOI_hash
perioada_before
perioada_after
```

### 5. OSM
Cheie:
```text
AOI_hash
categorie_osm
data_interogarii
```

Păstrează rezultate brute per categorie.

### 6. Statistici
Cheie:
```text
analysis_hash
buffer_m
```

### 7. Raport PDF
Cheie:
```text
analysis_hash
buffer_m
report_version
```

## Persistență

Folosește un director ignorat de Git:

```text
cache/
```

Recomandare:
- GeoJSON / Parquet pentru OSM;
- JSON pentru metadata;
- SQLite opțional pentru index;
- TTL configurabil pentru OSM.

## Invalidare selectivă

### Schimbare buffer
Recalculează numai:
- buffer;
- proximități OSM;
- statistici buffer;
- secțiunea relevantă din raport.

### Schimbare BEFORE / AFTER
Recalculează:
- apă SAR;
- Dynamic World;
- corelare;
- impact OSM;
- PDF.

### Schimbare AOI
Recalculează:
- scene;
- tile-uri;
- Dynamic World;
- OSM;
- statistici;
- PDF.

## Jurnal vizibil

Afișează:
```text
✓ Limite administrative încărcate din cache
✓ Scene Sentinel-1 disponibile în cache
✓ Date OSM încărcate din cache
→ Se recalculează impactul pentru bufferul de 250 m
```

## Teste

- cache hit;
- cache miss;
- TTL;
- invalidare după AOI;
- invalidare după scene;
- invalidare după buffer;
- `.gitignore`.

## La final

- rulează testele;
- verifică cache local;
- afișează `git diff --stat`;
- rulează `/review`;
- oprește-te înainte de commit.
