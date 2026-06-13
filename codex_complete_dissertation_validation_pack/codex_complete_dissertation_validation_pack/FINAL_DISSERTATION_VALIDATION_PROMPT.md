# Prompt Codex — validare finală pentru disertație

Lucrează în repository-ul local:

`geoint-flood-impact-dashboard`

Branch obligatoriu:

`review/dissertation-ready-local-run`

## Scop

Finalizează validarea tehnică a aplicației pentru disertație. Rulează aplicația local, verifică fluxul real pentru județul Galați, validează vizual rezultatele SAR, Dynamic World și OSM, generează raportul PDF, pregătește capturile necesare și actualizează pachetul tehnic destinat redactării părții scrise.

## Reguli obligatorii

- Nu inventa nicio valoare.
- Nu completa rezultate pe baza presupunerilor.
- Nu prezenta expunerea geometrică drept pagubă reală.
- Nu include token-uri, credentiale, conținutul fișierului `.env` sau identificatori sensibili.
- Nu face commit.
- Nu face push.
- Păstrează logurile locale.
- Dacă o verificare nu poate fi realizată, notează explicit: `[NEVALIDAT TEHNIC]`.
- Dacă o valoare necesită intervenție umană, notează: `[DECIZIE UMANĂ NECESARĂ]`.

---

# ETAPA 0 — Verificări inițiale

1. Confirmă branch-ul:

```powershell
git branch --show-current
```

Dacă branch-ul nu este:

```text
review/dissertation-ready-local-run
```

oprește-te și semnalează problema.

2. Creează directorul pentru loguri:

```powershell
New-Item -ItemType Directory -Force -Path .codex-sprint-logs | Out-Null
```

3. Salvează starea inițială:

```powershell
git status --short | Tee-Object -FilePath .codex-sprint-logs/final-validation-git-status-before.log
git diff --stat | Tee-Object -FilePath .codex-sprint-logs/final-validation-diff-before.log
```

4. Citește înainte de rulare:

```text
OVERNIGHT_HANDOFF.md
LOCAL_RUN_REPORT.md
TECHNICAL_HANDOFF_FOR_DISSERTATION.md
handoff/dissertation_final/README.md
handoff/dissertation_final/TECHNICAL_HANDOFF_FOR_DISSERTATION.md
handoff/dissertation_final/results_summary.json
handoff/dissertation_final/results_summary.csv
handoff/dissertation_final/READY_TO_INSERT_TEXT.md
handoff/dissertation_final/REMAINING_ISSUES.md
docs/screenshots/dissertation_final/README.md
```

5. Verifică existența:

```text
impact_tool.py
scripts/start_app.ps1
scripts/test_local_run.ps1
scripts/prepare_galati_cache.py
data/output/reports/
handoff/dissertation_final/
docs/screenshots/dissertation_final/
```

---

# ETAPA 1 — Teste automate și cache OSM Galați

1. Rulează verificarea completă locală:

```powershell
.\scripts\test_local_run.ps1 2>&1 |
    Tee-Object -FilePath .codex-sprint-logs/final-test-local-run.log
```

2. Rulează separat suita pytest:

```powershell
.\.venv\Scripts\python.exe -m pytest -q 2>&1 |
    Tee-Object -FilePath .codex-sprint-logs/final-pytest.log
```

3. Pregătește cache-ul Galați:

```powershell
.\.venv\Scripts\python.exe scripts\prepare_galati_cache.py 2>&1 |
    Tee-Object -FilePath .codex-sprint-logs/final-galati-cache.log
```

4. Verifică explicit status valid pentru:

```text
buildings
roads
railways
bridges
critical
critical_rapid
```

5. Rulează din nou cache-ul și cronometrează execuția:

```powershell
Measure-Command {
    .\.venv\Scripts\python.exe scripts\prepare_galati_cache.py 2>&1 |
        Tee-Object -FilePath .codex-sprint-logs/final-galati-cache-second-run.log
}
```

6. Confirmă dacă a doua rulare folosește cache-ul local și este mai rapidă.

Dacă apar erori:
- identifică exact categoria;
- verifică metadata cache;
- repară problema;
- rulează din nou;
- nu continua până când cache-ul nu este valid sau problema nu este documentată explicit.

---

# ETAPA 2 — Pornirea aplicației

1. Pornește aplicația:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\start_app.ps1
```

2. Verifică:

```text
http://127.0.0.1:8501
```

3. Verifică health endpoint:

```text
http://127.0.0.1:8501/_stcore/health
```

4. Confirmă:
- aplicația pornește;
- titlul este vizibil;
- statusul GEE este vizibil;
- sidebar-ul este vizibil;
- harta este încărcată;
- nu apar erori Python;
- nu apar erori JavaScript evidente;
- presetul Galați este disponibil.

5. Salvează rezultatul în:

```text
.codex-sprint-logs/browser-startup-validation.md
```

---

# ETAPA 3 — Fluxul real Galați

Rulează fluxul complet pentru presetul:

```text
Inundații Galați — septembrie 2024
```

1. Activează presetul Galați.

2. Confirmă:
- județul Galați;
- aria activă;
- intervalul temporal;
- polarizarea;
- direcția orbitei;
- starea cache-ului OSM;
- existența hărții.

3. Decide aria utilizată:
- județ complet;
sau
- AOI desenat manual.

Nu schimba aria fără justificare.

4. Notează:
- tipul ariei;
- suprafața;
- bbox;
- hash-ul ariei;
- data evenimentului;
- bufferul utilizat.

---

# ETAPA 4 — Selectarea și confirmarea scenelor Sentinel-1

1. Apasă:

```text
Caută scene Sentinel-1
```

2. Confirmă:
- galeria este vizibilă;
- thumbnail-urile sunt încărcate;
- cronologia este vizibilă;
- metadatele sunt afișate;
- butonul `Afișează mai multe` funcționează;
- nu există thumbnail-uri lipsă fără diagnostic.

3. Analizează scenele disponibile și selectează manual:
- o scenă BEFORE;
- o scenă AFTER.

4. Pentru rularea finală preferă obligatoriu:
- aceeași polarizare;
- același instrument mode;
- același orbit pass;
- aceeași orbită relativă;
- acoperire cât mai apropiată de 100%;
- scene apropiate temporal de eveniment.

5. Dacă nu există pereche perfect compatibilă:
- nu continua automat;
- listează opțiunile;
- notează avertismentele;
- marchează: `[DECIZIE UMANĂ NECESARĂ]`.

6. Apasă:

```text
Compară imaginile
```

7. Verifică sliderul:
- separator vertical;
- drag direct cu mouse-ul;
- BEFORE în stânga;
- AFTER în dreapta;
- fără slider orizontal;
- fără separator duplicat;
- fără layer gol.

8. Confirmă perechea numai după verificare vizuală.

9. Salvează în log:

```text
.codex-sprint-logs/final-sentinel1-selection.md
```

Include:
- ID scenă BEFORE;
- ID scenă AFTER;
- data și ora;
- polarizare;
- orbit pass;
- orbită relativă;
- acoperire;
- avertismente;
- motivul alegerii perechii.

---

# ETAPA 5 — Validarea pragului SAR

1. Folosește modul QA implementat în sprinturile SAR.

2. Pentru VH testează:

```text
-20 dB
-19 dB
-18 dB
-17 dB
-16 dB
```

Pentru VV testează:

```text
-17 dB
-16 dB
-15 dB
-14 dB
-13 dB
```

3. Pentru fiecare prag notează:
- apă BEFORE;
- apă AFTER;
- apă nouă;
- durată;
- status;
- diferența față de pragul echilibrat;
- observații vizuale.

4. Verifică manual:
- luciurile de apă existente;
- umbrele radar;
- zonele urbane;
- zonele de vegetație;
- artefactele de margine;
- suprafețele improbabile;
- discontinuitățile.

5. Alege pragul final numai după interpretarea rezultatelor.

6. Notează justificarea în:

```text
.codex-sprint-logs/final-sar-threshold-validation.md
```

Include tabelul:

```text
| Prag dB | Apă BEFORE km² | Apă AFTER km² | Apă nouă km² | Observații |
|---:|---:|---:|---:|---|
```

7. Dacă pragul nu poate fi justificat:
- nu completa valoarea finală;
- marchează: `[DECIZIE UMANĂ NECESARĂ]`.

---

# ETAPA 6 — Rularea analizei rapide

1. Configurează:
- pragul SAR final;
- smoothing;
- minimum connected pixels;
- buffer.

2. Rulează:

```text
Rulează analiza rapidă
```

3. Verifică:
- apă BEFORE;
- apă AFTER;
- apă nouă SAR;
- geometria vectorizată;
- bufferul;
- clădirile;
- drumurile;
- podurile;
- obiectivele critice;
- simbolurile;
- popup-urile;
- legenda;
- filtrarea layerelor;
- tabelul elementelor prioritare;
- sursa OSM;
- data cache-ului;
- completitudinea OSM;
- timpii.

4. Verifică vizual cel puțin:
- buffer 1 m;
- buffer 250 m;
- buffer 500 m;
- buffer 1000 m.

5. Nu interpreta automat elementele intersectate drept elemente avariate.

6. Salvează rezultatele în:

```text
.codex-sprint-logs/final-rapid-analysis.md
```

---

# ETAPA 7 — Rularea analizei detaliate

1. Rulează:

```text
Rulează analiza detaliată
```

2. Verifică:
- SAR BEFORE;
- SAR AFTER;
- apă nouă SAR;
- Dynamic World BEFORE;
- Dynamic World AFTER;
- schimbări Dynamic World;
- apă nouă Dynamic World;
- suprapunere SAR × Dynamic World;
- apă doar SAR;
- apă doar Dynamic World;
- OSM × Dynamic World;
- timpi;
- statusuri;
- erori tile;
- fallback mozaic, dacă este folosit.

3. Notează:
- perioada de căutare Dynamic World;
- data efectivă BEFORE;
- data efectivă AFTER;
- acoperirea;
- tipul produsului;
- eventualul fallback;
- erorile;
- limitările interpretării.

4. Verifică dacă Dynamic World este plauzibil vizual.

5. Dacă Dynamic World nu este disponibil:
- nu bloca rezultatul SAR;
- notează explicit eroarea;
- continuă raportarea prudentă.

6. Salvează rezultatele în:

```text
.codex-sprint-logs/final-detailed-analysis.md
```

---

# ETAPA 8 — Exportul rezultatelor pentru partea scrisă

Actualizează sau generează automat:

```text
data/output/final_run/results_summary.json
data/output/final_run/results_summary.csv
data/output/final_run/FINAL_GALATI_VALIDATION.md
```

Completează numai cu valori reale validate:

- repository;
- branch;
- commit;
- data rulării;
- aria;
- AOI;
- bbox;
- scenele Sentinel-1;
- polarizarea;
- orbita;
- acoperirea;
- pragul SAR;
- smoothing;
- minimum connected pixels;
- scara metricilor;
- scara vectorizării;
- bufferul;
- apa BEFORE;
- apa AFTER;
- apa nouă SAR;
- metricile Dynamic World;
- metricile OSM;
- obiectivele prioritare;
- timpii;
- cache-ul;
- statusurile;
- erorile;
- limitările;
- calea PDF.

Dacă un câmp nu poate fi validat, scrie:

```text
[NEVALIDAT TEHNIC]
```

Nu utiliza `0`, șir gol sau `None` pentru a ascunde o eroare.

---

# ETAPA 9 — Raportul PDF

1. Generează raportul PDF din aplicație.

2. Confirmă salvarea locală în:

```text
data/output/reports/
```

3. Copiază raportul validat în:

```text
handoff/dissertation_final/report/raport_geoint_inundatie_galati_final.pdf
```

4. Verifică:
- fișierul există;
- fișierul începe cu `%PDF`;
- numărul de pagini;
- coperta;
- aria analizată;
- scenele;
- parametrii;
- metricile SAR;
- Dynamic World;
- OSM;
- completitudinea;
- sursele;
- timpii;
- harta sintetică;
- scara;
- graficele;
- tabelele;
- diacriticele;
- nota obligatorie:

```text
Rezultatele reprezintă produse GEOINT preliminare de suport decizional
și nu constituie confirmare oficială din teren.
```

5. Dacă raportul nu este lizibil:
- identifică problema;
- repară generatorul;
- regenerează PDF-ul;
- repetă validarea.

6. Scrie:

```text
.codex-sprint-logs/final-pdf-validation.md
```

---

# ETAPA 10 — Capturi pentru disertație

Creează capturi PNG la minimum:

```text
1440 × 900
```

Salvează în:

```text
docs/screenshots/dissertation_final/
```

Fișiere obligatorii:

```text
01_interfata_initiala.png
02_preset_galati.png
03_selectare_scene_sentinel1.png
04_slider_before_after.png
05_parametri_sar.png
06_rezultat_sar.png
07_dynamic_world.png
08_corelare_sar_dynamic_world.png
09_osm_impact.png
10_osm_elemente_prioritare.png
11_raport_pdf_coperta.png
12_raport_pdf_harta.png
```

Reguli:
- nu include terminalul;
- nu include `.env`;
- nu include token-uri;
- nu include credentiale;
- nu include date personale;
- păstrează legendele lizibile;
- folosește zoom relevant;
- verifică vizual fiecare imagine.

Dacă browserul automat nu este disponibil:
- nu inventa capturi;
- păstrează fișierele `.txt`;
- creează:
  `.codex-sprint-logs/MANUAL_SCREENSHOT_CHECKLIST.md`;
- descrie exact pașii manuali rămași.

---

# ETAPA 11 — Actualizarea pachetului pentru disertație

Actualizează numai cu informații reale și validate:

```text
handoff/dissertation_final/TECHNICAL_HANDOFF_FOR_DISSERTATION.md
handoff/dissertation_final/results_summary.json
handoff/dissertation_final/results_summary.csv
handoff/dissertation_final/READY_TO_INSERT_TEXT.md
handoff/dissertation_final/REMAINING_ISSUES.md
handoff/dissertation_final/FIGURE_CAPTIONS.md
handoff/dissertation_final/PACKAGE_MANIFEST.md
```

Reguli:
- elimină marcajele `[DE COMPLETAT DUPĂ RULAREA FINALĂ]` numai dacă există valoare reală;
- păstrează `[NEVALIDAT TEHNIC]` dacă nu există confirmare;
- explică limitările;
- utilizează formulări prudente:
  - `apă observată automat prin SAR`;
  - `extindere preliminară`;
  - `element potențial expus`;
  - `intersectat geometric`;
  - `diferențe observate Dynamic World`;
  - `necesită verificare în teren`.

Nu utiliza:
- `pagubă confirmată`;
- `clădire inundată cert`;
- `drum distrus`;
- `rezultat oficial`;

decât dacă există o sursă externă independentă care confirmă afirmația.

---

# ETAPA 12 — Raport final Codex

Creează:

```text
.codex-sprint-logs/FINAL_DISSERTATION_VALIDATION_REPORT.md
```

Include:

1. branch;
2. commit;
3. sistem local;
4. versiune Python;
5. status GEE;
6. rezultate pytest;
7. rezultat health check;
8. cache OSM Galați;
9. scene Sentinel-1 finale;
10. compatibilitate scene;
11. prag SAR final;
12. justificarea pragului;
13. metrici SAR;
14. metrici Dynamic World;
15. metrici OSM;
16. timpi;
17. calea PDF;
18. număr pagini PDF;
19. lista capturilor;
20. probleme rămase;
21. decizii umane necesare;
22. pași pentru reproducerea analizei;
23. fișiere actualizate;
24. limitări metodologice.

La final afișează:

```powershell
git diff --stat
git status --short
```

Oprește-te înainte de commit și push.

---

# Condiții de finalizare

Taskul este finalizat numai dacă:

- cache-ul Galați este valid;
- testele trec;
- aplicația pornește;
- health check-ul trece;
- scenele finale sunt consemnate sau marcate explicit ca nevalidate;
- pragul SAR este justificat sau marcat drept decizie umană necesară;
- valorile reale sunt exportate fără presupuneri;
- PDF-ul este generat și verificat sau marcat explicit ca nevalidat;
- capturile sunt realizate sau există checklist manual;
- pachetul pentru partea scrisă este actualizat;
- raportul final Codex este creat;
- nu au fost expuse secrete;
- nu ai făcut commit;
- nu ai făcut push.
