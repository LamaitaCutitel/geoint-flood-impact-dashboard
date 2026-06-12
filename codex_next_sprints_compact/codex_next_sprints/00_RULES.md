# Reguli generale

- Lucrează numai în `feature/new-flood-impact-tool`.
- Nu extinde dashboard-ul vechi; reutilizează doar funcții stabile.
- Tool nou: fără JRC, DEM, slope, hillshade, NDVI, NDWI, MNDWI sau layere debug.
- SAR strict: `new water = AFTER - BEFORE`.
- AOI opțional; fără AOI se analizează județul complet.
- OSM se încarcă după analiza SAR.
- Analizează toate datele; afișează doar subseturi relevante.
- Coloana dreaptă este singurul control pentru layere tematice.
- Leaflet LayerControl păstrează doar basemap-uri și comparația BEFORE/AFTER.
- Păstrează tool-urile utile din stânga hărții.
- Buffer analitic: `1–1000 m`, implicit `250 m`.
- Buffer vizual clădiri de referință: fix `500 m`.
- Raport final: PDF.
- UI și raport: română.
- Folosește: `potențial expus`, `intersectat geometric`, `necesită verificare în teren`.
- Nu face commit și nu face push.
