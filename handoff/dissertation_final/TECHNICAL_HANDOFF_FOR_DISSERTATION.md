# Handoff tehnic pentru disertatie

## Identificare

- Branch: `review/dissertation-ready-local-run`
- Commit de baza: `a4e0837c53a2e42641bf08273eaab43e701ad374`
- Data validarii locale: 2026-06-13
- Judet: Galati
- Arie analizata: judet complet, 4465.5425 km2
- Buffer de avertizare: 250 m

## Scene Sentinel-1

- BEFORE:
  `COPERNICUS/S1_GRD/S1A_IW_GRDH_1SDV_20240902T042150_20240902T042215_055481_06C4C3_F4DF`
- AFTER:
  `COPERNICUS/S1_GRD/S1A_IW_GRDH_1SDV_20240914T042150_20240914T042215_055656_06CBAD_ACFC`
- Polarizare: VH
- Mod instrument: IW
- Directie: DESCENDING
- Orbita relativa: 109
- Acoperire: 95.9% pentru ambele scene
- Override-uri: niciunul

## Parametri finali

- Prag apa SAR: -18 dB, preset echilibrat
- Scara analiza raster: 10 m
- Scara vectorizare: 30 m
- Pixeli conectati minim: 8
- Suprafata minima poligon: 1000 m2
- Toleranta simplificare: 10 m
- Mod analiza: detaliat

## Rezultate tehnice

- Apa observata BEFORE prin SAR: 3256.9394 km2
- Apa observata AFTER prin SAR: 1550.6039 km2
- Extindere preliminara, apa nou observata automat prin SAR: 97.6628 km2
- Apa noua Dynamic World: 18.6308 km2
- Suprapunere SAR / Dynamic World: 1.1445 km2
- Numai SAR: 96.5184 km2
- Numai Dynamic World: 17.4863 km2

## Impact OSM

- Cladiri intersectate direct: 283
- Cladiri in buffer: 7075
- Cladiri complet intersectate: 48
- Cladiri partial intersectate: 235
- Drumuri intersectate direct: 58.017 km
- Cai ferate intersectate direct: 25.638 km
- Poduri intersectate direct: 0
- Obiective critice intersectate direct: 57
- Obiective critice in buffer: 300
- Sursa: cache local OSM valid pentru toate categoriile cerute

## Timpi

- SAR: 12.825 s
- Vectorizare: 9.719 s
- Dynamic World: 13.568 s
- Cache OSM: 6.925 s
- Impact OSM: 643.065 s
- QA SAR: 50.938 s
- Rulare detaliata completa observata: aproximativ 783 s

## Artefacte

- `results_summary.json`
- `results_summary.csv`
- `report/raport_geoint_inundatie_galati_final.pdf`
- PDF: 7 pagini, 605370 bytes, validare structurala reusita

## Formulare recomandata

Rezultatele reprezinta produse GEOINT preliminare de suport decizional.
Foloseste formularile `apa observata automat prin SAR`, `extindere
preliminara` si `diferente observate Dynamic World`. Nu prezenta rezultatul
drept inundatie confirmata.

## Validare manuala

Inspectia vizuala a hartii, a fiecarei pagini PDF si interpretarea
metodologica finala raman obligatorii.
