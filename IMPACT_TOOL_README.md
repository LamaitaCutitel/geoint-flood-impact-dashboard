# Tool pentru evaluarea impactului unei inundații

## Pornire

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-impact-tool.txt
.\.venv\Scripts\python.exe -m streamlit run impact_tool.py
```

Tool-ul este separat de dashboard-ul experimental din `app.py`.

## Flux

1. Selectează județul.
2. Desenează opțional un AOI; în lipsa lui este folosit județul complet.
3. Caută și confirmă exact două scene Sentinel-1.
4. Verifică scena BEFORE și AFTER cu separatorul vertical.
5. Rulează analiza SAR strict BEFORE/AFTER.
6. Verifică diferențele Dynamic World și corelarea multisursă.
7. Încarcă OSM după finalizarea SAR.
8. Ajustează bufferul de avertizare între 1 și 1000 m.
9. Generează raportul PDF.

## Arhitectură

Codul nou se află în `src/impact_tool/`. Procesarea raster rămâne în Google
Earth Engine. Local sunt păstrate numai metadate, GeoJSON OSM și rezultatele
necesare raportului.

## Cache

Directorul ignorat `cache/` conține metadate pentru scene, tile-uri, OSM,
statistici și rapoarte. Schimbarea bufferului invalidează numai impactul OSM,
statisticile dependente de buffer și raportul. Schimbarea scenelor sau AOI-ului
invalidează produsele dependente.

## Raport PDF

Raportul include scenele, metodologia, rezultatele SAR, Dynamic World,
corelarea, impactul OSM, o hartă sintetică, grafice, tabele, surse și limitări.
Nu se generează arhive ZIP.

## Limitări

- apa este observată automat prin SAR și nu reprezintă confirmare oficială;
- Dynamic World este o clasificare automată;
- completitudinea OSM variază geografic și temporal;
- diferențele de orbită și acoperire pot influența comparația;
- rezultatele necesită verificare în teren.
