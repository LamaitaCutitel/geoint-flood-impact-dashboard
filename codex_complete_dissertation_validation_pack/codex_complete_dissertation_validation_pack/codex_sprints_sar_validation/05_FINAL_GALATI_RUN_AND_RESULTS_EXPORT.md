# Sprint 5 — Rulare finală Galați și export rezultate

## Obiectiv
Execută fluxul real și generează valori utilizabile în disertație.

## Reguli
Nu inventa valori. Dacă browserul sau GEE nu sunt disponibile, oprește-te și marchează rezultatele ca nevalidate.

## Cache OSM obligatoriu
Rulează:

```powershell
New-Item -ItemType Directory -Force -Path .codex-sprint-logs | Out-Null
.\.venv\Scripts\python.exe scripts\prepare_galati_cache.py 2>&1 | Tee-Object -FilePath .codex-sprint-logs/galati-cache-final.log
```

Verifică status valid pentru:
- buildings;
- roads;
- railways;
- bridges;
- critical;
- critical_rapid.

## Pornire
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\start_app.ps1
```

## Flux manual asistat
- aplică presetul Galați;
- decide județ complet sau AOI;
- caută scene;
- selectează BEFORE și AFTER compatibile;
- compară vizual;
- confirmă perechea;
- justifică pragul folosind QA sweep;
- rulează analiza rapidă;
- rulează analiza detaliată;
- verifică layerele SAR, Dynamic World și OSM;
- generează PDF.

## Export automat
Adaugă butonul:
`Exportă pachetul tehnic al rulării`

Generează:
- `data/output/final_run/results_summary.json`;
- `data/output/final_run/results_summary.csv`;
- `data/output/final_run/FINAL_GALATI_VALIDATION.md`.

Include:
- commit;
- data rulării;
- scene;
- AOI/bbox;
- parametri;
- override-uri;
- metrici SAR;
- metrici Dynamic World;
- metrici OSM;
- timpi;
- statusuri;
- erori;
- calea PDF.

## Teste
- export fără valori inventate;
- export marchează lipsurile;
- JSON și CSV lizibile;
- status final separat de smoke test.
