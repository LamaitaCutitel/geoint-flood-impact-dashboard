# Technical Handoff for Dissertation

## 1. Scopul documentului

Acest document centralizează exclusiv informații validate tehnic și utile pentru redactarea părții scrise a disertației. Nu include valori finale ale studiului de caz, deoarece analiza Google Earth Engine completă cu selectarea manuală a scenelor Sentinel-1 nu a fost validată cap-coadă în browser.

Branch auditat: `review/dissertation-ready-local-run`  
Commit auditat: `abe48fb2102ad90c2577f1b33e40d78ddd61ef2f`

## 2. Starea validată a aplicației

Aplicația principală este separată de dashboard-ul experimental și pornește prin entrypoint-ul:

```text
impact_tool.py
```

Acesta apelează interfața principală din:

```text
src/impact_tool/ui/shell.py
```

Dashboard-ul vechi `app.py` este păstrat doar ca instrument experimental și nu reprezintă metodologia principală a disertației.

## 3. Arhitectura aplicației

Structura principală este modulară:

- `src/impact_tool/ui/` — interfața Streamlit, sidebar, exploratorul scenelor și taburile de rezultate;
- `src/impact_tool/map/` — harta Folium/Leaflet, layerele, legenda, controalele de navigare și comparatoarele;
- `src/impact_tool/sar.py` — analiza Sentinel-1 SAR;
- `src/impact_tool/dynamic_world.py` — analiza Dynamic World și corelarea multisursă;
- `src/impact_tool/osm.py` — interogarea, parsarea și cache-ul OpenStreetMap;
- `src/impact_tool/osm_impact.py` — clasificarea impactului geometric direct și în buffer;
- `src/impact_tool/report.py` — generarea raportului PDF;
- `src/gee/` — integrarea Google Earth Engine;
- `scripts/` — pornire locală, verificare, export și pregătirea cache-ului Galați.

## 4. Metodologia SAR implementată

Metodologia principală utilizează două scene Sentinel-1 individuale:

- o scenă `BEFORE`;
- o scenă `AFTER`.

Analiza principală este strictă:

```text
apă nouă SAR = apă AFTER − apă BEFORE
```

Aplicația nu utilizează JRC în metodologia noului tool. Rezultatul trebuie formulat prudent ca produs GEOINT preliminar de suport decizional, nu ca o confirmare oficială din teren.

Utilizatorul poate:

1. selecta județul;
2. desena opțional un AOI;
3. căuta scene Sentinel-1;
4. vizualiza thumbnail-uri;
5. selecta manual scenele `BEFORE` și `AFTER`;
6. compara scenele în aceeași hartă printr-un separator vertical;
7. confirma perechea;
8. rula analiza rapidă sau detaliată.

## 5. Exploratorul Sentinel-1

Exploratorul temporal este afișat în zona principală a paginii. Sunt implementate:

- căutarea scenelor Sentinel-1;
- afișarea cronologiei;
- afișarea scenei curente;
- thumbnail mare și galerie cu mai multe carduri;
- încărcare progresivă a thumbnail-urilor;
- cache PNG local cu TTL;
- selecție manuală `BEFORE` și `AFTER`;
- previzualizare pe hartă;
- validarea compatibilității perechii;
- butoane separate pentru comparare, confirmare, ieșire din comparație și curățarea selecției.

Comparatorul scenelor folosește un separator vertical deplasat direct prin drag pe hartă.

## 6. AOI și hartă interactivă

AOI-ul este opțional. În lipsa unui AOI, analiza se execută pe județul complet. Un AOI desenat este validat și devine aria activă.

Harta interactivă include:

- basemap `OSM Light / CartoDB Positron`;
- basemap `Satelit / Esri World Imagery`;
- limitele județelor fără umplere de culoare;
- evidențierea județului selectat;
- selecția județului prin click;
- desenarea AOI-ului;
- măsurarea distanței și suprafeței;
- revenire la România;
- centrare pe județ;
- centrare pe AOI;
- fullscreen;
- identificarea coordonatelor;
- legendă pentru layerele active.

## 7. Moduri de analiză

Sunt implementate două moduri:

### Mod rapid

Rulează:

- analiza SAR;
- încărcarea categoriilor OSM operaționale;
- evaluarea clădirilor;
- evaluarea drumurilor;
- evaluarea podurilor;
- evaluarea obiectivelor critice;
- clasificarea directă și în buffer.

Dynamic World este omis intenționat în acest mod.

### Mod detaliat

Rulează:

- analiza SAR;
- Dynamic World;
- corelarea multisursă;
- toate categoriile OSM disponibile;
- clasificarea impactului OSM;
- datele necesare raportului extins.

## 8. Dynamic World

Dynamic World este utilizat opțional pentru:

- observația `BEFORE`;
- observația `AFTER`;
- diferențele observate;
- apa nouă identificată prin Dynamic World;
- suprapunerea cu rezultatul SAR;
- apa identificată numai prin SAR;
- apa identificată numai prin Dynamic World.

Selecția observației ține cont de acoperirea AOI-ului și proximitatea temporală. Dacă acoperirea observației individuale este sub `85%`, aplicația utilizează un mozaic fallback. În interfață sunt raportate perioada de căutare, data efectivă, acoperirea și tipul produsului.

## 9. OpenStreetMap

Datele OSM sunt încărcate după analiza SAR. Aplicația utilizează cache persistent și indică sursa datelor în interfață.

Pentru presetul Galați, cache-ul este pregătit pentru județul Galați extins cu `1000 m`.

Categoriile validate prin scriptul local sunt:

- `buildings`;
- `roads`;
- `railways`;
- `bridges`;
- `critical`;
- `critical_rapid`.

Aplicația distinge între:

- elemente intersectate direct;
- elemente aflate în bufferul de avertizare;
- elemente de context;
- clădiri de referință.

Bufferul configurabil este cuprins între `1 m` și `1000 m`, cu valoare implicită `250 m`.

Clădirile de referință sunt limitate la maximum `750` de elemente și sunt selectate din proximitatea elementelor afectate. Pentru infrastructura liniară sunt separate geometriile directe, geometriile din buffer și segmentele de context.

## 10. Cache OSM Galați

Pregătirea cache-ului se execută prin:

```powershell
.\.venv\Scripts\python.exe scripts\prepare_galati_cache.py
```

Scriptul verifică:

- limita administrativă Galați;
- extinderea cu `1000 m`;
- cache-ul persistent;
- completitudinea fiecărei categorii;
- existența metadatelor valide;
- categoria critică pentru modul rapid.

Scriptul oprește execuția dacă o categorie este lipsă, incompletă sau invalidă.

## 11. Raport PDF

Raportul PDF este generat local prin ReportLab și salvat în:

```text
data/output/reports/
```

Raportul include:

- copertă;
- județ și AOI;
- buffer;
- scenele Sentinel-1 `BEFORE` și `AFTER`;
- metodologia SAR;
- indicatorii SAR;
- statusul Dynamic World;
- corelarea SAR × Dynamic World;
- impactul OSM;
- corelarea OSM × Dynamic World;
- completitudinea OSM;
- hartă sintetică;
- grafice separate pe tipuri de unități;
- tabele detaliate;
- limitări;
- surse;
- parametri tehnici;
- duratele etapelor;
- informații despre cache.

Raportul include explicit nota:

```text
Rezultatele reprezintă produse GEOINT preliminare de suport decizional și nu constituie confirmare oficială din teren.
```

## 12. Verificări automate validate

În rularea locală documentată au trecut:

- importurile Python;
- verificarea fișierelor obligatorii;
- pregătirea cache-ului OSM Galați;
- suita pytest completă;
- Streamlit health check;
- detectarea configurației locale GEE;
- exportul curat fără secrete, cache, medii virtuale sau rastere mari.

Rularea locală documentată a utilizat:

- Python `3.12.7`;
- port smoke test `8510`;
- durată totală `35.66 secunde`;
- export curat de `2.68 MiB`, cu `230` intrări și zero potriviri sensibile.

În predarea overnight a fost consemnată rularea a `211` teste pytest.

GitHub Actions a finalizat cu succes workflow-ul `Impact tool CI`, care include:

- instalarea dependențelor;
- import curat;
- rularea testelor;
- Streamlit startup smoke test.

## 13. Verificări structurale validate pentru PDF

Testele automate validează:

- generarea unui fișier PDF;
- generarea raportului și cu rezultate parțiale;
- suportul pentru AOI;
- suportul pentru buffer `1 m` și `1000 m`;
- cache-ul raportului;
- invalidarea cheii cache când se modifică payload-ul analitic;
- utilizarea geometriei decupate pentru infrastructura liniară;
- generarea hărții sintetice offline;
- includerea unei scări geodezice;
- separarea graficelor pe unități;
- denumirea raportului folosind data evenimentului când aceasta este disponibilă;
- afișarea lizibilă a erorilor Dynamic World.

## 14. Limitări validate

Următoarele limitări trebuie menționate în lucrare:

- rezultatele SAR depind de geometria achiziției și de rugozitatea suprafeței;
- Dynamic World este o clasificare automată și poate avea decalaje temporale față de scena SAR;
- completitudinea datelor OSM poate varia;
- analiza reprezintă o evaluare preliminară;
- rezultatele necesită verificare în teren;
- analiza completă necesită autentificare Google Earth Engine și acces la internet;
- Overpass API este utilizat când cache-ul OSM local nu este disponibil.

## 15. Elemente care nu sunt încă validate și nu trebuie prezentate ca rezultate finale

Nu sunt încă validate:

- scenele Sentinel-1 finale selectate pentru studiul de caz;
- valorile reale calculate pentru suprafața apei;
- valorile reale privind clădirile și infrastructura potențial expuse;
- rularea GEE completă cap-coadă în browser;
- verificarea vizuală a layerelor Dynamic World cu date reale;
- verificarea vizuală a raportului PDF cu date reale;
- capturile finale pentru disertație;
- comparația cu observații din teren.

Până la validarea manuală, în lucrare se folosesc marcaje de tipul:

```text
[DE COMPLETAT DUPĂ VALIDAREA FLUXULUI GALAȚI]
```

## 16. Capturi necesare pentru disertație

Capturile trebuie salvate în:

```text
docs/screenshots/dissertation/
```

Lista obligatorie:

1. `01-startup.png` — ecran inițial cu titlul, statusul GEE, județul Galați și harta României;
2. `02-scene-selection.png` — galeria Sentinel-1 cu scenele `BEFORE` și `AFTER` selectate;
3. `03-before-after-swipe.png` — comparatorul vertical activ;
4. `04-sar-results.png` — rezultatul SAR, extinderea preliminară și bufferul activ;
5. `05-dynamic-world.png` — datele efective Dynamic World și diferențele observate;
6. `06-osm-impact.png` — elementele OSM, sursa datelor și tabelul de priorități;
7. `07-pdf-report.png` — coperta și harta sintetică din raportul PDF.

Capturile nu trebuie să includă terminalul, fișierul `.env`, credentiale, token-uri sau date personale.

## 17. Sprinturi recomandate înainte de folosirea rezultatelor finale în disertație

Sprinturile de mai jos sunt recomandări operaționale, nu rezultate științifice:

1. Validarea manuală a fluxului Galați în browser: preset, cache, selecție scene, comparație, analiză rapidă, analiză detaliată.
2. Alegerea și notarea scenelor Sentinel-1 finale `BEFORE` și `AFTER`.
3. Generarea capturilor din `docs/screenshots/dissertation/README.md`.
4. Generarea și verificarea vizuală a raportului PDF cu rezultate reale.
5. Transferul în disertație numai al valorilor calculate și verificate manual.

## 18. Reguli pentru redactarea disertației

În partea scrisă sunt recomandate formulările:

- `apă observată automat prin SAR`;
- `extindere preliminară`;
- `element potențial expus`;
- `intersectat geometric`;
- `diferențe observate Dynamic World`;
- `necesită verificare în teren`.

Trebuie evitate formulările care prezintă rezultatele automate drept confirmări oficiale ale situației din teren.
