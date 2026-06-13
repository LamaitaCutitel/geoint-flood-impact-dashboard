# Sprint 4 — Cache OSM, status și prewarm Galați

## Obiectiv
Asigură cache local valid și status corect pentru OSM.

## Modificări
- Păstrează calea absolută pentru cache:
  - `PROJECT_ROOT / "cache"`;
  - opțional `GEOINT_CACHE_DIR`.
- Aplicația și scriptul de prewarm trebuie să folosească aceeași cale.
- Aria Galați:
  - județ + `1000 m`.
- `osm_complet` numai dacă:
  - toate categoriile au `ok=True`;
  - toate au `completeness == "complet"`.
- Altfel:
  - `osm_parțial`;
  - afișează categoria și motivul.
- Separă statusurile:
  - SAR reușit;
  - OSM complet;
  - OSM parțial;
  - OSM indisponibil;
  - impact geometric indisponibil.
- Nu afișa mesaj verde fals.

## Rulare obligatorie cache OSM
Creează folderul log dacă lipsește:

```powershell
New-Item -ItemType Directory -Force -Path .codex-sprint-logs | Out-Null
```

Rulează:

```powershell
python scripts/prewarm_galati_cache.py 2>&1 | Tee-Object -FilePath .codex-sprint-logs/osm-prewarm-galati.log
```

Verifică:
- exit code `0`;
- status `valid` pentru:
  - buildings;
  - roads;
  - railways;
  - bridges;
  - critical;
  - critical_rapid;
- lipsa `RuntimeError`.

Rulează din nou:

```powershell
python scripts/prewarm_galati_cache.py 2>&1 | Tee-Object -FilePath .codex-sprint-logs/osm-prewarm-galati-second-run.log
```

Confirmă că a doua rulare folosește cache-ul și este mai rapidă.

## Teste
- cache comun aplicație/prewarm;
- status complet/parțial;
- prewarm valid;
- al doilea prewarm mai rapid.
