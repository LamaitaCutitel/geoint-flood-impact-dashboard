# Reguli generale

- Lucrează numai în noul tool.
- Nu modifica dashboard-ul vechi decât pentru reutilizarea controlată a unor funcții stabile.
- Nu introduce JRC, DEM, slope, hillshade, NDVI, NDWI sau MNDWI.
- SAR rămâne strict `BEFORE`, `AFTER`, `new water = AFTER - BEFORE`.
- AOI este opțional; fără AOI se analizează județul complet.
- OSM se procesează după SAR.
- Coloana din dreapta este singurul control pentru layere tematice.
- Controlul Leaflet din hartă păstrează doar două basemap-uri și comparația BEFORE/AFTER.
- Păstrează tool-urile utile din stânga hărții.
- Buffer analitic: `1–1000 m`, implicit `250 m`.
- Buffer vizual clădiri de referință: `500 m`.
- UI și raport: română.
- Folosește formulări prudente: `potențial expus`, `intersectat geometric`, `necesită verificare în teren`.
- Nu face commit și nu face push.
