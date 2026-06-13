# Sprint 3 — Metrici SAR și vectorizare coerentă

## Obiectiv
Aliniază rasterul, metricile și geometria folosită în impactul OSM.

## Probleme
- Metricile folosesc implicit `10 m`.
- Vectorizarea folosește fix `30 m` și `bestEffort=True`.
- Geometria OSM poate diferi de rasterul și suprafața raportate.

## Modificări
- Adaugă:
  - `analysis_scale_meters`;
  - `vectorization_scale_meters`;
  - `minimum_polygon_area_m2`;
  - `geometry_simplification_tolerance_m`.
- Folosește implicit aceeași scară pentru metrici și vectorizare dacă performanța permite.
- Dacă vectorizarea necesită scară mai grosieră:
  - consemnează diferența;
  - afișează avertisment;
  - păstrează rasterul ca produs autoritativ pentru suprafață.
- Înregistrează folosirea `bestEffort`.
- Elimină poligoanele foarte mici înainte de impactul OSM.
- Păstrează:
  - raster autoritativ;
  - geometrie vectorială operațională OSM;
  - geometrie simplificată pentru hartă.
- Grupează metricile SAR într-un singur apel GEE multi-band dacă este posibil.

## Teste
- scările sunt exportate;
- avertisment la scări diferite;
- poligoane mici eliminate;
- metricile nu necesită trei apeluri separate;
- OSM folosește geometria operațională.
