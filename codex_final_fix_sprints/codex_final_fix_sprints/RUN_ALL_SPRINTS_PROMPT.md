# Prompt Codex — rulare toate sprinturile

Lucrează în repository-ul local `geoint-flood-impact-dashboard`, pe branch-ul `feature/new-flood-impact-tool`.

Citește:
1. `codex_final_fix_sprints/README.md`
2. `codex_final_fix_sprints/00_RULES.md`

Rulează sprinturile `01`–`05` strict în ordine.

Reguli:
- implementează un singur sprint la un moment dat;
- citește doar regulile generale și sprintul curent;
- rulează testele relevante;
- dacă sprintul afectează UI-ul, pornește aplicația și verifică startup-ul;
- oprește-te dacă apare o eroare nereparată;
- salvează rezumat în `.codex-sprint-logs/<numar>-summary.md`;
- nu face commit;
- nu face push.

După ultimul sprint:
- rulează toate testele;
- pornește `python -m streamlit run impact_tool.py`;
- generează `.codex-sprint-logs/FINAL_REPORT.md`;
- afișează `git diff --stat`;
- afișează `git status --short`;
- oprește-te înainte de commit și push.
