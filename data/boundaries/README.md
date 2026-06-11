# Boundaries

`romania_counties.geojson` contine limitele administrative NUTS 2024 level 3
pentru Romania, filtrate din Eurostat GISCO:

https://gisco-services.ec.europa.eu/distribution/v2/nuts/geojson/NUTS_RG_01M_2024_4326_LEVL_3.geojson

Fisierul este folosit pentru harta initiala a Romaniei si pentru AOI-ul judetului
selectat.

- Data descarcarii/pregatirii locale: 2026-06-03.
- CRS: EPSG:4326.
- Camp nume judet utilizat in aplicatie: `NAME_LATN`.
- Camp tara utilizat pentru filtrare: `CNTR_CODE = RO`.

Pentru inlocuire, pastrati acelasi format GeoJSON `FeatureCollection` si asigurati
existenta unui camp de nume compatibil (`NAME_LATN`, `NUTS_NAME` sau `NAME`).

Do not commit sensitive data, large rasters, or generated outputs. The first
version uses the county dropdown as the primary AOI selection method.
