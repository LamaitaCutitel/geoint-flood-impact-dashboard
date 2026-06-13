# Prompt Codex — rulează toate sprinturile

Lucrează în repository-ul local `geoint-flood-impact-dashboard`,
pe branch-ul `review/dissertation-ready-local-run`.

Citește:
1. `codex_sprints_sar_validation/README.md`
2. `codex_sprints_sar_validation/00_RULES.md`

Rulează sprinturile `01`–`07` strict în ordine.

Pentru fiecare sprint:
- citește numai sprintul curent;
- implementează numai sprintul curent;
- rulează testele cerute;
- scrie `.codex-sprint-logs/<numar>-summary.md`;
- afișează `git diff --stat` și `git status --short`;
- oprește-te dacă există erori nereparate;
- nu face commit;
- nu face push.

Pentru Sprintul 5:
- rulează obligatoriu `scripts/prepare_galati_cache.py`;
- execută fluxul real Galați numai dacă browserul și GEE sunt disponibile;
- nu inventa valori;
- oprește-te și marchează `[NEVALIDAT TEHNIC]` dacă validarea reală nu este posibilă.

După Sprintul 7:
- rulează toate testele;
- generează `.codex-sprint-logs/FINAL_SAR_VALIDATION_REPORT.md`;
- afișează `git diff --stat`;
- afișează `git status --short`;
- oprește-te înainte de commit și push.
