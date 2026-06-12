# Sprint 7 — QA final

## Obiectiv
Verifică demonstrația Galați de la cap la coadă.

## Rulare obligatorie cache OSM
Rulează din nou:

```powershell
New-Item -ItemType Directory -Force -Path .codex-sprint-logs | Out-Null
python scripts/prewarm_galati_cache.py 2>&1 | Tee-Object -FilePath .codex-sprint-logs/osm-prewarm-final.log
```

Nu continua dacă scriptul eșuează.

## Teste automate
Rulează:

```powershell
python -m pytest -q
```

## Smoke test
Pornește:

```powershell
python -m streamlit run impact_tool.py --server.headless true --server.address 127.0.0.1 --server.port 8501
```

Verifică:

```text
http://127.0.0.1:8501/_stcore/health
```

## Checklist manual
- preset Galați;
- cache valid;
- galerie mare;
- thumbnail-uri;
- selecție BEFORE/AFTER;
- comparație direct drag;
- confirmare;
- analiză rapidă;
- OSM vizibil;
- clădiri;
- drumuri;
- poduri;
- obiective;
- filtre;
- legendă;
- analiză detaliată;
- Dynamic World;
- comparator tematic ↔;
- buffer 1/250/500/1000;
- AOI;
- PDF.

## Raport
Creează:

```text
.codex-sprint-logs/FINAL_QA.md
```

Include:
- fișiere modificate;
- teste;
- timpi;
- prewarm;
- categorii validate;
- limitări;
- pași de pornire.

## Final
Afișează:

```powershell
git diff --stat
git status --short
```

Oprește-te înainte de commit și push.
