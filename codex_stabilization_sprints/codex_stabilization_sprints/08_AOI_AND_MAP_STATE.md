# Sprint 8 — AOI și stare hartă

## Obiectiv
Corectează validarea AOI și rerandarea hărții.

## Modificări
- AOI: Shapely `intersects` și `intersection`.
- Nu valida doar după vertecși.
- Suprafață AOI metrică prin `pyproj`.
- Render hash hartă include:
  - buffer;
  - preview scene;
  - preview mode;
  - filtre OSM;
  - critical mode;
  - presentation mode;
  - focus location.
- Pentru `Zoom`: `setView([lat, lon], 17)` și reset focus.
- Păstrează tool-urile stânga: home România, center județ, center AOI, draw, measure, identify, fullscreen.

## Teste
- AOI mare care intersectează județul;
- AOI decupat;
- rerandare după buffer și filtre;
- Zoom unic.
