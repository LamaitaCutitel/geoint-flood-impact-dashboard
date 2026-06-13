# Reguli generale

- Lucrează numai în noul tool.
- Nu modifica dashboard-ul vechi decât pentru reutilizarea controlată a UX-ului stabil.
- Backend-ul nou rămâne sursa principală.
- SAR strict: `BEFORE`, `AFTER`, `new water = AFTER - BEFORE`.
- AOI opțional; fără AOI se analizează județul complet.
- Nu introduce JRC, DEM, slope, hillshade, Sentinel-2, NDVI, NDWI sau MNDWI.
- LayerControl din hartă păstrează doar basemap-urile.
- Coloana din dreapta controlează layerele tematice.
- Buffer analitic: `1–1000 m`, implicit `250 m`.
- Buffer vizual clădiri de referință: `500 m`.
- UI și PDF: română.
- Nu face commit.
- Nu face push.
