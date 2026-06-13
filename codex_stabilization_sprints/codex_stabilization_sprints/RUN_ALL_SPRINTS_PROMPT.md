# Prompt Codex — toate sprinturile

Lucrează în repository-ul local `geoint-flood-impact-dashboard`, pe branch-ul `feature/new-flood-impact-tool`.

Citește:
1. `codex_stabilization_sprints/README.md`
2. `codex_stabilization_sprints/00_RULES.md`

Rulează sprinturile `01`–`10` strict în ordinea din README.

Reguli:
- citește doar regulile generale și sprintul curent;
- implementează un singur sprint la un moment dat;
- rulează testele relevante după fiecare sprint;
- oprește-te dacă testele eșuează și nu poți repara stabil problema;
- nu trece peste erori;
- salvează după fiecare sprint `.codex-sprint-logs/<numar>-summary.md`;
- nu face commit;
- nu face push.

După ultimul sprint:
- rulează toate testele;
- pornește `python -m streamlit run impact_tool.py`;
- generează `.codex-sprint-logs/FINAL_REPORT.md`;
- afișează `git diff --stat`;
- afișează `git status --short`;
- oprește-te înainte de commit și push.
