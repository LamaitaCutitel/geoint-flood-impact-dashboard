# Ghid rapid pentru review

## Scop

Aplicatia principala este `impact_tool.py`. Ea sustine o evaluare GEOINT
preliminara pe baza unei perechi de scene Sentinel-1 individuale BEFORE/AFTER,
Dynamic World si date OpenStreetMap.

Rezultatele folosesc formularile prudente `apa observata automat prin SAR`,
`extindere preliminara` si `diferente observate Dynamic World`. Aplicatia nu
confirma o inundatie in teren.

## Pornire rapida pe Windows

Cerinta recomandata: Python 3.12, Git si un cont Google Earth Engine autorizat.

```powershell
git clone <URL_REPOSITORY>
cd geoint-flood-impact-dashboard
git switch review/dissertation-ready-local-run
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\start_app.ps1
```

Scriptul creeaza `.venv` cu Python 3.12 daca nu exista, instaleaza dependentele,
verifica starea GEE si porneste aplicatia la `http://127.0.0.1:8501`.

Pentru autentificarea initiala GEE:

```powershell
.\.venv\Scripts\python.exe -m src.gee.gee_auth
```

ID-ul proiectului se configureaza local prin `GEE_PROJECT_ID`; nu este versionat
niciun secret.

## Flux demonstrativ Galati

1. Selecteaza presetul Galati.
2. Verifica geometria judetului si, optional, deseneaza un AOI.
3. Cauta si selecteaza o scena BEFORE si una AFTER.
4. Confirma perechea si activeaza comparatia.
5. Ruleaza analiza rapida sau detaliata.
6. Verifica layerele SAR, diferentele Dynamic World si elementele OSM.
7. Genereaza PDF-ul. O copie este salvata in `data/output/reports/`.

Pregatirea cache-ului OSM:

```powershell
.\.venv\Scripts\python.exe scripts\prepare_galati_cache.py
```

## Verificare automata

```powershell
.\test_local_run.ps1
```

Raportul este actualizat in `LOCAL_RUN_REPORT.md`.

## Export curat

```powershell
.\export_for_review.ps1
```

Cache-ul OSM este exclus implicit. Pentru un pachet offline mai mare:

```powershell
.\export_for_review.ps1 -IncludeOsmCache
```
