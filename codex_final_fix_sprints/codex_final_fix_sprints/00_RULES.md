# Reguli generale

- Lucrează numai în noul tool.
- Nu modifica dashboard-ul vechi decât pentru reutilizarea controlată a unor funcții stabile.
- Nu adăuga JRC, DEM, slope, hillshade, NDVI, NDWI sau MNDWI.
- SAR rămâne strict `BEFORE`, `AFTER`, `new water = AFTER - BEFORE`.
- AOI este opțional; fără AOI se analizează județul complet.
- OSM se procesează după SAR.
- Buffer analitic: `1–1000 m`, implicit `250 m`.
- Buffer vizual clădiri de referință: `500 m`.
- Coloana dreaptă controlează layerele tematice.
- LayerControl din hartă păstrează doar basemap-urile.
- Păstrează tool-urile Leaflet din stânga.
- UI și PDF: română.
- Nu face commit și nu face push.
