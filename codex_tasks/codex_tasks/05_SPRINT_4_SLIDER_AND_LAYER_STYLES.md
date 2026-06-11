# Sprint 4 — Slider stabil și stiluri centralizate

## Obiectiv

Elimină conflictele de slider și centralizează culorile.

## Slider

Păstrează:
- slider standard pentru comparația implicită;
- control custom doar pentru schimbarea perechii.

Elimină:
- controale duplicate;
- polling infinit;
- reconstruiri inutile.

Adaugă:
- timeout plugin Leaflet;
- fallback clar;
- eliminarea controlului anterior;
- păstrarea zoom-ului;
- verificare că separatorul este vizibil și glisabil.

## Stiluri

Creează:

```python
LAYER_STYLES = {
  "sar_new_water": {
    "display_name": "...",
    "vis_params": {...},
    "legend_color": "...",
    "description": "...",
    "category": "..."
  }
}
```

Folosește aceeași sursă pentru:
- tile URL;
- legendă;
- registry;
- raport.

## Restricții

- nu modifica algoritmii raster;
- nu adăuga OSM;
- nu adăuga EMS.

## La final

- rulează `pytest`;
- afișează `git diff --stat`;
- rulează `/review`;
- oprește-te înainte de commit.
