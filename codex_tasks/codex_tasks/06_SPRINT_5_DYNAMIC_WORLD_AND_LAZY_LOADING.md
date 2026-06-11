# Sprint 5 — Dynamic World și lazy loading

## Obiectiv

Sincronizează Dynamic World cu scena AFTER și redu timpul de încărcare.

## Dynamic World AFTER

Adaugă:
```text
- Interval complet
- Fereastră apropiată de scena SAR AFTER
```

Default:
```text
Fereastră apropiată de scena SAR AFTER
```

Reguli:
- fereastră ±1–3 zile;
- fallback interval complet;
- salvează perioada exactă în legendă și raport.

## Layere imediate

```text
SAR BEFORE
SAR AFTER
SAR water BEFORE
SAR water AFTER
SAR new water
SAR flood extent filtrat
Dynamic World BEFORE
Dynamic World AFTER
Dynamic World new water
SAR × Dynamic World overlap
JRC permanent water
```

## Layere la cerere

```text
SAR difference
SAR ratio
SAR persistent water
SAR water loss
Dynamic World other changes
RGB
NDWI
MNDWI
NDVI
NDMI
DEM
slope
hillshade
```

Adaugă:
```text
Încarcă layere suplimentare
```

Nu rerula analiza principală pentru tile-uri suplimentare.

## La final

- rulează `pytest`;
- afișează `git diff --stat`;
- rulează `/review`;
- oprește-te înainte de commit.
