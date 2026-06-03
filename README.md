# GEOINT Flood Impact Dashboard

Dashboard web interactiv pentru cartografierea rapida si preliminara a inundatiilor
folosind imagini Sentinel-1 SAR procesate in Google Earth Engine.

Proiectul sustine disertatia „Aplicarea tehnologiilor GEOINT pentru sprijinirea
interventiilor in situatii de urgenta si protectia mediului”.

## Scop

Aplicatia produce o extindere preliminara detectata automat prin SAR si calculeaza
tipuri de teren intersectate de extinderea detectata. Rezultatul este un produs
GEOINT preliminar de suport decizional, potrivit pentru demonstratii academice si
analize rapide.

## Arhitectura

- Streamlit ruleaza local interfata, parametrii, harta si rapoartele mici.
- Google Earth Engine proceseaza rasterele Sentinel-1, JRC Global Surface Water,
  Dynamic World si Sentinel-2.
- Folium si streamlit-folium afiseaza tile layers generate in cloud.
- Rapoartele locale sunt JSON, CSV, HTML si TXT.

## Dataset-uri

- `COPERNICUS/S1_GRD` pentru SAR before/after si change detection.
- `JRC/GSW1_4/GlobalSurfaceWater` pentru apa permanenta.
- `GOOGLE/DYNAMICWORLD/V1` pentru terenuri intersectate.
- `COPERNICUS/S2_SR_HARMONIZED` pentru context RGB optional.
- Eurostat GISCO NUTS 2024 level 3 pentru limitele administrative ale judetelor
  Romaniei, salvat local in `data/boundaries/romania_counties.geojson`.

## Functionalitati

- Preset `Galati - September 2024 Floods`.
- Harta initiala a Romaniei disponibila imediat, chiar fara Google Earth Engine.
- Dropdown pentru selectarea judetului, implicit `Galati`.
- Evidentierea judetului selectat, tooltip, popup si zoom automat pe bounding box.
- Status servicii si jurnal live de initializare vizibile la pornire.
- Parametri Sentinel-1: polarizare, orbit pass, smoothing, prag, pixeli conectati.
- Profile de analiza: Rapid preview, Standard, Detailed export.
- Slider vertical before/after cu `folium.plugins.SideBySideLayers`.
- Fallback documentat cand layer-ele GEE nu sunt disponibile.
- Tabel si bar chart pentru terenuri intersectate de extinderea preliminara detectata.
- Rapoarte mici in `data/output/reports/`.

## Capturi Placeholder

Adaugati capturi dupa prima rulare locala:

- Dashboard principal.
- Slider before/after SAR.
- Layer detected flood extent.
- Panou statistici land cover.

## Instalare Rapida

Recomandat: Python 3.12 sau 3.13. Evita Python 3.14 pentru aceasta versiune,
deoarece unele pachete geospatiale cu extensii native pot avea roti binare
incompatibile.

```powershell
git clone https://github.com/LamaitaCutitel/geoint-flood-impact-dashboard.git
cd geoint-flood-impact-dashboard
py -3.12 -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
```

Editati `.env` si setati `GEE_PROJECT_ID`.

```powershell
python -m src.gee.gee_auth
streamlit run app.py
```

Autentificarea Earth Engine se face o singura data pe fiecare PC sau VM.
Interfata se incarca si fara autentificare GEE, permitand explorarea hartii
administrative si a parametrilor. Analiza SAR este declansata doar dupa butonul
`Ruleaza analiza SAR`.

## Limitari

Aplicatia nu inlocuieste Copernicus EMS, nu confirma situatia din teren, nu ruleaza
modele hidraulice si nu prezice precipitatii. Nu exista integrare ANAR in aceasta
versiune.

Rezultatele reprezinta produse GEOINT preliminare de suport decizional. Extinderea
detectata automat prin Sentinel-1 SAR poate diferi de situatia reala din teren din
cauza momentului achizitiei, rezolutiei spatiale, pragurilor utilizate, zgomotului
radar, vegetatiei si limitarilor datelor auxiliare.

## Roadmap

Vezi [ROADMAP.md](ROADMAP.md).
