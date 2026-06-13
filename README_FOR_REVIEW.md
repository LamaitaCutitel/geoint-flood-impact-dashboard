# Ghid rapid pentru review

## Scop

Aplicatia principala este `impact_tool.py`. Ea sustine o evaluare GEOINT
preliminara pe baza unei perechi de scene Sentinel-1 individuale BEFORE/AFTER,
Dynamic World si date OpenStreetMap.

Rezultatele folosesc formularile prudente `apa observata automat prin SAR`,
`extindere preliminara` si `diferente observate Dynamic World`. Aplicatia nu
confirma o inundatie in teren.

## Arhitectura si directoare

- `impact_tool.py` este entrypoint-ul principal.
- `src/impact_tool/` contine starea, workflow-ul, UI-ul, harta, SAR, Dynamic
  World, OSM si raportul PDF.
- `src/gee/` contine integrarea Google Earth Engine.
- `data/boundaries/` contine limita administrativa locala necesara pornirii.
- `cache/` si `data/output/` sunt generate local si nu sunt versionate.
- `tests/` contine suita pytest.

## Pornire rapida pe Windows

Cerinta recomandata: Python 3.12, Git si un cont Google Earth Engine autorizat.

```powershell
git clone <URL_REPOSITORY>
cd geoint-flood-impact-dashboard
git switch review/dissertation-ready-local-run
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\start_app.ps1
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
.\scripts\test_local_run.ps1
```

Raportul este actualizat in `LOCAL_RUN_REPORT.md`.

## Export curat

```powershell
.\scripts\export_for_review.ps1
```

Cache-ul OSM este exclus implicit. Pentru un pachet offline mai mare:

```powershell
.\scripts\export_for_review.ps1 -IncludeOsmCache
```

Arhiva standard este `export_review/Disertatie_GEOINT_App_Review.zip`.

## Stare si limitari cunoscute

Functiile finalizate sunt inventariate in `TECHNICAL_STATUS.md`. Verificarile
locale sunt in `LOCAL_RUN_REPORT.md`, iar predarea completa in
`OVERNIGHT_HANDOFF.md`.

Analiza completa necesita autentificare GEE si acces la internet. Overpass poate
avea timeout cand cache-ul local lipseste. Capturile si continutul PDF cu date
reale trebuie verificate manual in browser.
