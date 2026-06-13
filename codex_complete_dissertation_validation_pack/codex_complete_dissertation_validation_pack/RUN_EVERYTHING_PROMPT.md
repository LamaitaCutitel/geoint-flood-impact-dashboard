# Prompt Codex — rulează sprinturile și validarea finală

Lucrează în repository-ul local:

`geoint-flood-impact-dashboard`

Branch obligatoriu:

`review/dissertation-ready-local-run`

În repository există folderul:

`codex_complete_dissertation_validation_pack/`

## Ordine obligatorie

1. Citește:
   - `codex_complete_dissertation_validation_pack/codex_sprints_sar_validation/README.md`
   - `codex_complete_dissertation_validation_pack/codex_sprints_sar_validation/00_RULES.md`

2. Rulează sprinturile `01`–`07` strict în ordinea indicată în README.

3. După fiecare sprint:
   - citește numai fișierul sprintului curent;
   - implementează numai sprintul curent;
   - rulează testele cerute;
   - scrie `.codex-sprint-logs/<numar>-summary.md`;
   - afișează `git diff --stat`;
   - afișează `git status --short`;
   - oprește-te dacă există erori nereparate;
   - nu face commit;
   - nu face push.

4. După finalizarea sprinturilor, citește:
   - `codex_complete_dissertation_validation_pack/FINAL_DISSERTATION_VALIDATION_PROMPT.md`

5. Execută validarea finală locală și actualizează pachetul pentru disertație.

## Reguli

- Nu inventa valori.
- Nu completa rezultate fără rulare reală.
- Nu expune secrete.
- Nu continua peste erori critice.
- Nu face commit.
- Nu face push.
- Dacă browserul sau GEE nu permit validarea completă, marchează explicit:
  `[NEVALIDAT TEHNIC]`.
- Dacă este necesară alegerea utilizatorului, marchează:
  `[DECIZIE UMANĂ NECESARĂ]`.

## Final

După toate etapele:
- rulează testele complete;
- afișează `git diff --stat`;
- afișează `git status --short`;
- generează `.codex-sprint-logs/FINAL_DISSERTATION_VALIDATION_REPORT.md`;
- oprește-te înainte de commit și push.
