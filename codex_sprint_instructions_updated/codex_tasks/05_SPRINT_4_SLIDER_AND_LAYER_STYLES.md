# Sprint 4 — Slider stabil și catalog unic de stiluri

## Obiectiv

Elimină conflictele dintre controalele de comparație și centralizează culorile.

## Partea A — Slider

Păstrează:

- slider standard pentru comparația implicită;
- control custom numai pentru alegerea altor perechi după analiză.

Elimină:

- controale side-by-side duplicate;
- reconstruiri inutile;
- polling infinit pentru plugin.

Adaugă:

- timeout la încărcarea pluginului Leaflet;
- mesaj de fallback;
- eliminarea controlului anterior înainte de reconstruire;
- păstrarea zoom-ului și centrului;
- verificare explicită că separatorul este vizibil și glisabil.

## Partea B — Stiluri

Creează un catalog unic:

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

Elimină mapările duplicate ale culorilor.

## Restricții

- nu modifica algoritmii raster;
- nu adăuga OSM;
- nu adăuga EMS.

## Teste

Adaugă teste pentru:

- absența controalelor duplicate;
- ordine default SAR BEFORE / AFTER;
- fallback dacă pluginul nu se încarcă;
- consistența dintre hartă și legendă;
- registry.

## Verificare manuală

1. compară candidați BEFORE / AFTER;
2. glisează separatorul;
3. ieși din comparație;
4. pornește din nou comparația;
5. rulează analiza;
6. schimbă perechea finală;
7. verifică legenda.

## La final

- rulează `pytest`;
- afișează `git diff --stat`;
- rulează `/review`;
- nu face push;
- oprește-te.
