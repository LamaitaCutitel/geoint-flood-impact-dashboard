# Sprint 3 — Comparatoare separate

## Obiectiv
Separă complet compararea scenelor de compararea rezultatelor tematice.

## Comparator scene
- Disponibil înainte de analiză.
- Buton `Compară imaginile`.
- Folosește doar:
  - Sentinel-1 SAR BEFORE;
  - Sentinel-1 SAR AFTER;
  - opțional măști apă BEFORE/AFTER.
- Drag direct pe bara verticală.
- Fără slider orizontal.
- Se închide după confirmarea scenelor sau schimbarea perechii.

## Comparator rezultate
- Disponibil după analiză.
- Adaugă tool Leaflet în bara stângă, similar MeasureControl.
- Icon: `↔`.
- Deschide mini-panou:
  - layer stânga;
  - layer dreapta;
  - preset;
  - activează;
  - închide.
- Layere eligibile:
  - SAR BEFORE;
  - SAR AFTER;
  - apă nouă SAR;
  - Dynamic World BEFORE;
  - Dynamic World AFTER;
  - schimbări Dynamic World;
  - apă nouă Dynamic World;
  - ambele metode;
  - doar SAR;
  - doar Dynamic World;
  - basemap satelit;
  - basemap OSM Light.
- Preseturi:
  - SAR BEFORE ↔ SAR AFTER;
  - Dynamic World BEFORE ↔ Dynamic World AFTER;
  - apă nouă SAR ↔ apă nouă Dynamic World;
  - satelit ↔ apă nouă SAR.

## Stare
Adaugă stări separate:
- `scene_compare_active`;
- `scene_compare_tiles`;
- `layer_compare_active`;
- `layer_compare_left_id`;
- `layer_compare_right_id`.

Regulă:
- cele două comparatoare nu pot fi active simultan;
- bara nu apare fără două tile URL valide;
- la eroare afișează mesaj clar;
- păstrează centrul și zoom-ul hărții.

## Teste
- comparator scene independent;
- comparator tematic independent;
- un singur divider activ;
- fără divider dacă lipsește tile URL;
- preseturi funcționale;
- tool Leaflet vizibil în stânga.
