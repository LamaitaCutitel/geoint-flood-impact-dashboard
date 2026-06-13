# File Manifest pentru review

## Entrypoint si configurare

- `impact_tool.py` - aplicatia principala pentru disertatie.
- `requirements.txt` - dependentele generale.
- `requirements-impact-tool.txt` - dependentele explicite ale tool-ului nou.
- `pytest.ini` - colectare limitata la suita sursa, fara exporturi generate.
- `.env.example` - numele variabilei GEE, fara valoare secreta.

## Cod principal

- `src/impact_tool/` - stare, workflow, SAR, Dynamic World, OSM, harta, UI si PDF.
- `src/gee/` - autentificare si procesare Google Earth Engine reutilizata.
- `src/app/county_boundaries.py` - limite administrative reutilizate.
- `data/boundaries/romania_counties.geojson` - limite locale pentru pornire.

## Scripturi

- `scripts/start_app.ps1` - instalare si pornire locala.
- `scripts/test_local_run.ps1` - teste, cache OSM si health check Streamlit.
- `scripts/export_for_review.ps1` - arhiva curata si manifest SHA-256.
- `scripts/prepare_galati_cache.py` - validarea/pregatirea cache-ului OSM Galati.

## Documentatie

- `README_FOR_REVIEW.md`
- `TECHNICAL_STATUS.md`
- `SECURITY_REVIEW.md`
- `SCREENSHOT_GUIDE.md`
- `LOCAL_RUN_REPORT.md`
- `OVERNIGHT_HANDOFF.md`

## Excluse intentionat

`.env`, medii virtuale, token-uri, fisiere de credentiale, cache-uri, rezultate,
arhive, GeoTIFF-uri si loguri brute. Lista completa este in `.gitignore`.
