# Codex sprint pack — Tool nou pentru evaluarea impactului unei inundații

Acest folder conține instrucțiuni incrementale pentru construirea unui tool nou, separat și clar, în repository-ul existent:

```text
geoint-flood-impact-dashboard
```

Tool-ul nou trebuie să fie orientat strict spre analiza impactului unei inundații și să evite aglomerarea produsă de layere tehnice greu de explicat.

## Scopul tool-ului

Aplicația trebuie să răspundă clar la întrebările:

1. Unde exista apă înainte de eveniment?
2. Unde există apă după eveniment?
3. Unde a apărut apă nouă?
4. Ce tipuri de teren au devenit apă conform Dynamic World?
5. Ce clădiri și elemente de infrastructură OSM sunt intersectate direct?
6. Ce elemente se află în bufferul de avertizare?
7. Ce rezultat poate fi prezentat clar într-un raport PDF?

## Reguli metodologice definitive

- fără JRC Global Surface Water;
- analiza SAR este strict BEFORE / AFTER;
- utilizatorul selectează exact două scene Sentinel-1;
- layerul principal este `Apă nouă evidențiată prin SAR`;
- impactul OSM se calculează pe baza apei noi SAR și a bufferului;
- Dynamic World se afișează BEFORE / AFTER și prin modificările observate;
- AOI este opțional:
  - dacă există AOI desenat, se analizează AOI-ul;
  - dacă nu există AOI, se analizează întreg județul;
- datele OSM se încarcă după rularea analizei SAR;
- bufferul este controlat prin slider 1–1000 m;
- bufferul este afișat pe hartă ca poligon foarte transparent;
- aplicația trebuie să folosească cache persistent și invalidare selectivă;
- raportul final este PDF, nu ZIP;
- interfața trebuie să fie în limba română;
- sliderul glisant BEFORE / AFTER rămâne obligatoriu.

## Imaginea de referință UI

Folosește:

```text
reference_ui/evaluare_impact_inundatie_mockup.png
```

ca reper vizual pentru structură, claritate și distribuția elementelor în pagină.

Nu copia pixel-perfect. Reproduce:
- antetul;
- coloana stângă cu pașii și controalele;
- harta centrală dominantă;
- panoul din dreapta cu layere grupate și legendă simplă;
- cardurile cu indicatori;
- graficele;
- butonul de raport PDF.

## Cum se folosesc sprinturile

Nu executa toate sprinturile într-o singură sesiune.

Pentru fiecare sprint:
1. pornește Codex CLI în repository;
2. cere-i să citească fișierul sprintului;
3. implementează numai cerințele acelui sprint;
4. rulează testele;
5. verifică manual aplicația;
6. rulează `/diff`;
7. rulează `/review`;
8. fă commit;
9. treci la sprintul următor.

Exemplu prompt:

```text
Citește fișierul codex_new_tool/sprints/03_SPRINT_2_AOI_AND_STATE.md și implementează numai cerințele din el.
Nu trece la sprintul următor.
La final rulează testele, afișează git diff --stat și oprește-te înainte de commit.
```

## Ordinea sprinturilor

1. `00_PROJECT_RULES.md`
2. `01_AUDIT_EXISTING_CODE.md`
3. `02_SPRINT_1_NEW_TOOL_SHELL.md`
4. `03_SPRINT_2_AOI_AND_STATE.md`
5. `04_SPRINT_3_CACHE_ARCHITECTURE.md`
6. `05_SPRINT_4_SAR_SCENE_SELECTION_AND_SWIPE.md`
7. `06_SPRINT_5_STRICT_SAR_BEFORE_AFTER_ANALYSIS.md`
8. `07_SPRINT_6_DYNAMIC_WORLD_ANALYSIS.md`
9. `08_SPRINT_7_OSM_LOADING_AFTER_ANALYSIS.md`
10. `09_SPRINT_8_OSM_IMPACT_BUFFER_AND_SYMBOLS.md`
11. `10_SPRINT_9_OPTIONAL_MAP_TOOLS.md`
12. `11_SPRINT_10_PDF_REPORT.md`
13. `12_SPRINT_11_PERFORMANCE_AND_FINAL_POLISH.md`
14. `checklists/MANUAL_TEST_CHECKLIST.md`
15. `checklists/COMMIT_TEMPLATE.md`
