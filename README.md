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
- O singura harta interactiva folosita pentru selectia judetului, explorarea temporala SAR si rezultatele finale.
- Explorator temporal Sentinel-1 SAR pentru cautarea scenelor disponibile fara rularea analizei finale.
- Selectie manuala a perechii SAR BEFORE/AFTER, cu validare de compatibilitate.
- Comparatie vizuala a candidatilor BEFORE/AFTER inainte de analiza finala, fara flood detection.
- Harta initiala a Romaniei disponibila imediat, chiar fara Google Earth Engine.
- Dropdown pentru selectarea judetului, implicit `Galati`.
- Harta porneste centrat pe Romania; dupa selectie, click pe judet sau dropdown, face zoom pe judetul selectat.
- Evidentierea judetului selectat prin contur, fara umplere colorata, tooltip si popup.
- Status servicii si jurnal live de initializare vizibile la pornire.
- AOI-ul analizei foloseste geometria reala a judetului, iar bounding box-ul este folosit doar pentru zoom.
- Parametri Sentinel-1: polarizare, orbit pass, smoothing, prag SAR change,
  prag separat pentru detectia SAR water si pixeli conectati.
- Analiza finala foloseste implicit scenele individuale selectate manual; compozitul median ramane optiune avansata dezactivata implicit.
- Sentinel-2 RGB si indici NDWI, MNDWI, NDVI, NDMI pentru before/after si diferente.
- Dynamic World before/after, diferente observate intre compozitele analizate si terenuri intersectate.
- SAR water BEFORE/AFTER, SAR new water, apa persistenta SAR si pierdere de apa SAR.
- Dynamic World apa noua, pierdere apa si suprapunere cu SAR new water.
- Layere de corelare: SAR x Dynamic World new water overlap, New water only SAR
  si New water only Dynamic World.
- Masca JRC configurabila: Conservator, Echilibrat sau Extins.
- DEM SRTM, hillshade si slope ca layere auxiliare.
- Profile de analiza: Rapid preview, Standard, Detailed export.
- Layer registry central pentru LayerControl, raport si comparatii.
- Slider vertical before/after SAR water pornit automat dupa analiza finala, plus control in harta `Compara doua layere` pentru perechi alternative fara rerulare GEE.
- Legenda in harta pentru limite administrative, layere incarcate si perioadele before/after folosite la preluarea datelor.
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

## Harta Unica Si Layere

Aplicatia foloseste o singura harta Folium/Leaflet. La pornire, harta afiseaza
judetele Romaniei pe un basemap color, centrata pe Romania. Selectia se poate face
prin click pe judet sau din dropdown; dupa selectie, harta se centreaza pe judetul
selectat. Dupa cautarea Sentinel-1, aceeasi harta afiseaza doar scena curenta din
timeline sau perechea candidata BEFORE/AFTER, decupata dupa geometria judetului.
Dupa analiza finala, aceeasi harta primeste layere GEE decupate dupa geometria
judetului selectat:

- Sentinel-1 SAR before, after, diferenta, raport si extindere preliminara detectata.
- SAR water BEFORE/AFTER, SAR new water, apa persistenta SAR, pierdere de apa SAR
  si SAR flood extent filtrat.
- Sentinel-2 RGB before/after si indici NDWI, MNDWI, NDVI, NDMI.
- Dynamic World before/after si diferente observate intre compozitele analizate.
- Dynamic World new water si suprapuneri cu SAR new water.
- Apa permanenta JRC, DEM, hillshade si slope.

Layerele pot fi activate/dezactivate din LayerControl. Bara verticala before/after
SAR water este adaugata automat cand cele doua layere SAR water BEFORE/AFTER sunt disponibile.
Controlul `Compara doua layere` din harta permite alegerea altor doua layere
comparabile pentru bara verticala glisanta, fara procesare GEE noua. Legenda din
harta afiseaza sursele si perioadele before/after folosite pentru datele incarcate.

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
