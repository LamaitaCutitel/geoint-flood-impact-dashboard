# Instrucțiuni Codex pentru `geoint-flood-impact-dashboard`

Acest folder conține task-uri incrementale pentru stabilizarea și extinderea proiectului.

## Regula principală

Nu executa toate sprinturile într-o singură sesiune.

Flux recomandat:

1. Deschide terminalul în repository.
2. Pornește Codex CLI:
   ```powershell
   codex
   ```
3. Pentru fiecare sprint:
   - cere-i să citească fișierul curent;
   - lasă-l să implementeze numai cerințele acelui fișier;
   - rulează testele;
   - verifică vizual aplicația;
   - rulează `/diff`;
   - rulează `/review`;
   - fă commit;
   - treci la sprintul următor.

## Ordinea fișierelor

1. `00_AGENTS_MD_UPDATE.md`
2. `01_AUDIT_ONLY.md`
3. `02_SPRINT_1_STATE_RESET.md`
4. `03_SPRINT_2_RECOMMENDATIONS_AND_GEE_ERRORS.md`
5. `04_SPRINT_3_HYBRID_SAR_STRATEGY.md`
6. `05_SPRINT_4_SLIDER_AND_LAYER_STYLES.md`
7. `06_SPRINT_5_DYNAMIC_WORLD_AND_LAZY_LOADING.md`
8. `07_FULL_MANUAL_TEST_CHECKLIST.md`
9. `08_SPRINT_6_OSM_OPERATIONAL_IMPACT.md`
10. `09_SPRINT_7_EMS_VALIDATION.md`
11. `11_SPRINT_8_UI_LEGEND_OSM_REPORT.md`
12. `10_COMMIT_AND_PUSH_TEMPLATE.md`

## Cum îi ceri lui Codex să citească un fișier

Exemplu:

```text
Citește fișierul codex_tasks/02_SPRINT_1_STATE_RESET.md și execută numai cerințele din el.
Nu trece la sprintul următor.
La final rulează testele, raportează git diff și oprește-te înainte de commit.
```

## Recomandare Git

Lucrează pe branch-uri separate:

```powershell
git checkout -b feature/stabilize-raster-workflow
```

După stabilizarea rasterului:

```powershell
git checkout -b feature/osm-operational-impact
```

Pentru validare EMS:

```powershell
git checkout -b feature/ems-validation
```
