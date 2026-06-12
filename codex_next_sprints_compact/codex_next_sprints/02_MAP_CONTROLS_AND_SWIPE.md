# Sprint 2 — Control hartă și Swipe

## Obiectiv
Elimină conflictul dintre controalele layerelor.

## Modificări
- Leaflet LayerControl: doar `OSM Light / CartoDB Positron` și `Satelit / Esri World Imagery`.
- Layere tematice: `control=False`.
- Coloana dreaptă controlează SAR, Dynamic World, OSM și buffer.
- Păstrează tool-urile stânga: zoom, home România, center județ/AOI, draw AOI, measure, identify, fullscreen.
- Păstrează un singur slider vertical BEFORE/AFTER.
- Moduri: radar grayscale și mască apă SAR.

## Teste
Fără duplicate, două basemap-uri, swipe unic și glisabil, tool-uri funcționale.
