# Overnight Handoff

Data: 2026-06-13

## Branch

`review/dissertation-ready-local-run`

## Obiectiv

Pregatirea unei versiuni demonstrabile si reproductibile local pentru evaluarea
disertatiei, fara secrete sau fisiere generate mari in Git.

## Implementat

- delimitarea clara intre tool-ul principal si dashboard-ul experimental;
- metodologie SAR cu scene individuale BEFORE/AFTER;
- cache OSM Galati validat si sursa afisata in UI;
- raport PDF salvat local;
- scripturi de pornire, test si export;
- documentatie de review si audit de securitate.

## De verificat manual

- autentificarea GEE pe calculatorul evaluatorului;
- selectia scenelor si comparatorul vertical;
- rularea completa SAR si Dynamic World;
- vizibilitatea layerelelor active;
- continutul raportului PDF cu date reale;
- capturile din `SCREENSHOT_GUIDE.md`.

## Comenzi

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\start_app.ps1
.\test_local_run.ps1
.\export_for_review.ps1
```

## Limitari

Rezultatul reprezinta o extindere preliminara si necesita verificare in teren.
Disponibilitatea GEE, Dynamic World si Overpass depinde de autentificare si retea.
