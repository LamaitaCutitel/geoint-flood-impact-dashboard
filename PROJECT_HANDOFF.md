# PROJECT_HANDOFF

## Scop

`geoint-flood-impact-dashboard` este o aplicatie Streamlit pentru analiza
preliminara a inundatiilor cu Sentinel-1 SAR in Google Earth Engine.

## Structura

- `app.py`: intrarea Streamlit.
- `config/settings.py`: constante, preset Galati, validare parametri.
- `src/gee/`: autentificare si procesare GEE.
- `src/app/`: layout, harti, jurnal, rezultate.
- `src/reports/`: generare JSON, CSV, HTML si log.
- `src/utils/`: utilitare locale.
- `tests/`: teste pytest pentru logica locala si fallback-uri.

## Functionalitati Implementate

- Configurare GEE prin `.env`.
- Preset Galati September 2024.
- Colectii Sentinel-1 before/after.
- Compozite mediane si smoothing.
- Detectie SAR ratio cu prag configurabil.
- Masca JRC pentru apa permanenta.
- Intersectare Dynamic World.
- Harta Folium cu layer control.
- Slider vertical before/after cu fallback.
- Rapoarte JSON, CSV, HTML si TXT.

## Dataset-uri

- `COPERNICUS/S1_GRD`
- `JRC/GSW1_4/GlobalSurfaceWater`
- `GOOGLE/DYNAMICWORLD/V1`
- `COPERNICUS/S2_SR_HARMONIZED`

## Rulare

```powershell
copy .env.example .env
python -m src.gee.gee_auth
streamlit run app.py
```

## Roadmap

Vezi `ROADMAP.md`.
