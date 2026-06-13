# Codex sprint pack compact — UX Sentinel-1 și OSM

Repository: `LamaitaCutitel/geoint-flood-impact-dashboard`
Branch: `feature/new-flood-impact-tool`

## Ordine
1. `00_RULES.md`
2. `01_RESTORE_SENTINEL_EXPLORER.md`
3. `02_SCENE_COMPARATOR_AND_STATE.md`
4. `03_LAYERS_LEGEND_COUNTY_CLICK.md`
5. `04_OSM_CACHE_STATUS_AND_PREWARM.md`
6. `05_OSM_VISIBLE_RESULTS_AND_PERFORMANCE.md`
7. `06_DYNAMIC_WORLD_AND_PDF.md`
8. `07_FINAL_QA.md`

Rulează un singur sprint într-o sesiune Codex.

După fiecare sprint:
- rulează testele relevante;
- verifică `git diff --stat`;
- verifică `git status --short`;
- scrie rezumat în `.codex-sprint-logs/<numar>-summary.md`;
- oprește-te înainte de commit și push.

## Când rulezi cache-ul OSM
Nu rula scriptul după fiecare sprint.

Rulează obligatoriu:
1. la finalul sprintului `04_OSM_CACHE_STATUS_AND_PREWARM.md`;
2. din nou în sprintul `07_FINAL_QA.md`.
