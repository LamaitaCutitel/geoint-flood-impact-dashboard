# Sprint 8 — Interfață coerentă, legendă utilă, layere grupate și raport HTML profesional

## Obiectiv

Îmbunătățește interfața și raportarea fără să schimbi algoritmii raster deja implementați.

Acest sprint trebuie rulat după stabilizarea sliderului, stilurilor și încărcării lazy.

---

## 1. Legendă simplificată și relevantă

Problema actuală:
- legenda este prea încărcată;
- afișează prea multe detalii simultan;
- nu explică suficient ce reprezintă culorile interne ale layerelor tematice.

### Cerință

Înlocuiește legenda lungă cu o legendă contextuală, minimizabilă și dependentă de layer-ele active.

Afișează implicit numai:
- numele layerului activ;
- tipul rezultatului;
- sursa;
- data sau perioada;
- explicația culorilor;
- pragurile relevante;
- un buton sau control pentru extinderea detaliilor.

### Exemple

Pentru `SAR new water`:

```text
SAR new water
Sursa: Sentinel-1 SAR
Perioadă: BEFORE → AFTER
■ cyan — apă observată în AFTER, absentă în BEFORE
```

Pentru `Dynamic World BEFORE / AFTER`:

```text
Dynamic World land cover
■ albastru — water
■ verde închis — trees
■ verde deschis — grass
■ mov-albăstrui — flooded vegetation
■ portocaliu — crops
■ galben — shrub and scrub
■ roșu — built
■ gri — bare
■ mov deschis — snow and ice
```

Pentru `Dynamic World changes`:

```text
Dynamic World changes
■ albastru intens — apă nouă
■ portocaliu — pierdere apă
■ mov discret — alte diferențe observate
■ transparent — fără schimbare
```

Pentru `SAR × Dynamic World overlap`:

```text
Corelare multisursă
■ verde intens — apă nouă identificată de ambele metode
■ cyan — apă nouă identificată doar prin SAR
■ mov — apă nouă identificată doar prin Dynamic World
```

### Reguli

- folosește un singur catalog central `LAYER_STYLES`;
- fiecare layer trebuie să aibă:
  - `display_name`;
  - `category`;
  - `vis_params`;
  - `legend_items`;
  - `description`;
  - `source`;
  - `date_or_period`;
  - `layer_type`;
- legenda și tile URL-urile trebuie să citească din același catalog;
- nu afișa metadate tehnice lungi implicit;
- mută detaliile tehnice într-un expander;
- legenda trebuie să fie minimizabilă;
- legenda trebuie să se actualizeze după activarea sau dezactivarea layerelor.

---

## 2. Gruparea layerelor

Problema actuală:
- prea multe layere apar într-o singură listă;
- utilizatorul găsește greu layer-ele relevante;
- interfața devine aglomerată.

### Cerință

Grupează layer-ele în categorii clare folosind un control Leaflet grupat sau un control custom stabil.

### Categorii

```text
Administrative
- Romania counties
- Selected county

SAR exploration
- Candidate BEFORE
- Candidate AFTER
- SAR grayscale preview
- SAR water preview

SAR water analysis
- SAR water BEFORE
- SAR water AFTER
- SAR new water
- SAR flood extent filtered

Dynamic World
- Dynamic World BEFORE
- Dynamic World AFTER
- Dynamic World new water
- SAR × Dynamic World overlap

Optional SAR layers
- SAR difference
- SAR ratio
- SAR persistent water
- SAR water loss

Optional optical layers
- RGB BEFORE
- RGB AFTER
- NDWI
- MNDWI
- NDVI
- NDMI

Optional terrain layers
- DEM
- hillshade
- slope

OSM operational impact
- Exposed buildings
- Critical facilities
- Intersected roads
- Intersected railways
- Intersected bridges
```

### Reguli

- implicit încarcă numai layer-ele esențiale;
- layer-ele opționale se încarcă prin butonul `Load additional layers`;
- nu genera tile URL pentru layer-ele opționale înainte să fie cerute;
- păstrează doar 2–4 layere active implicit;
- controlul trebuie să permită extinderea și restrângerea categoriilor;
- nu încărca simultan toate layerele OSM dacă nu sunt solicitate.

---

## 3. Simboluri OSM pentru obiective critice

Problema:
- obiectivele critice nu trebuie afișate ca puncte generice.

### Cerință

Pentru layerul `Critical facilities`, folosește simboluri diferențiate și ușor de înțeles.

### Simboluri recomandate

```text
Hospital / clinic         → cruce medicală
Fire station              → simbol pompieri / flacără
Police station            → scut
School                    → simbol educație
Emergency services        → simbol intervenție
Pharmacy                  → cruce medicală mică
Fuel station              → pompă carburant
Bridge                    → simbol pod
```

### Reguli

- folosește iconuri Leaflet / Font Awesome / BeautifyIcon disponibile local sau prin integrarea existentă;
- adaugă fallback la marker simplu dacă iconul nu se poate încărca;
- popup-ul trebuie să afișeze:
  - tip obiectiv;
  - nume;
  - sursă OSM;
  - distanță față de extinderea preliminară;
  - status: `intersected`, `within buffer`, `outside`;
- adaugă legendă separată pentru simbolurile OSM;
- folosește formularea `potentially exposed`, nu `affected with certainty`.

---

## 4. O singură limbă în interfață

Problema:
- interfața amestecă română și engleză.

### Cerință

Alege o singură limbă pentru UI și aplic-o peste tot.

### Recomandare

Folosește română pentru versiunea actuală a disertației.

Înlocuiește textele mixte:

```text
BEFORE / AFTER
SAR water
new water
persistent water
water loss
layer
overlap
flood extent
```

cu formulări românești clare, păstrând termenii tehnici între paranteze unde este util.

### Exemple recomandate

```text
Imagine de referință (BEFORE)
Imagine după eveniment (AFTER)
Apă observată prin SAR înainte de eveniment
Apă observată prin SAR după eveniment
Apă nouă evidențiată prin SAR
Apă persistentă observată prin SAR
Pierdere de apă observată prin SAR
Extindere preliminară filtrată
Suprapunere SAR × Dynamic World
Încarcă layere suplimentare
Mod prezentare
```

### Reguli

- toate butoanele;
- toate heading-urile;
- toate tooltip-urile;
- toate mesajele de eroare;
- legenda;
- raportul HTML;
- exporturile;
- popup-urile OSM;
- tab-urile;
- logurile vizibile utilizatorului

trebuie să folosească aceeași limbă.

Poți păstra în cod ID-uri interne în engleză.

---

## 5. Tooltips pentru toți parametrii

Fiecare parametru vizibil trebuie să aibă explicație.

### Structura tooltip-ului

Pentru fiecare control explică:
1. ce reprezintă;
2. cum influențează rezultatul;
3. când se modifică;
4. care este valoarea recomandată implicit;
5. ce risc apare dacă este setat greșit.

### Parametri obligatorii

- polarizare;
- orbit pass;
- data evenimentului;
- interval BEFORE;
- interval AFTER;
- metoda BEFORE;
- metoda AFTER;
- SAR change threshold;
- SAR water threshold;
- smoothing radius;
- minimum connected pixels;
- mod mască JRC;
- scară analiză;
- Dynamic World window;
- buffer OSM;
- profil de performanță;
- încărcare layere suplimentare.

### Exemplu

```text
Prag apă SAR:
Controlează identificarea pixelilor radar cu semnal compatibil cu apa.
Un prag mai sensibil evidențiază mai multe zone, dar poate include umbre radar,
sol umed sau suprafețe netede. Valoarea implicită Echilibrat este recomandată
pentru prima analiză.
```

---

## 6. Raport HTML profesional

Problema:
- raportul actual este tehnic și simplu;
- nu este suficient de clar pentru prezentare academică.

### Cerință

Generează un raport HTML profesional, lizibil și structurat.

### Structură recomandată

```text
1. Titlu și metadate
2. Rezumat executiv
3. Zona analizată
4. Date utilizate
5. Perechea Sentinel-1 selectată
6. Metodologia SAR
7. Rezultate principale
8. Dynamic World
9. Corelare multisursă
10. Impact operațional OSM
11. Grafice
12. Limitări
13. Jurnal metodologic sumar
14. Surse de date
15. Anexă tehnică
```

### Rezumat executiv

Afișează concis:

- județ;
- data evenimentului;
- scene BEFORE / AFTER;
- metodă BEFORE;
- metodă AFTER;
- suprafață apă nouă SAR;
- suprafață Dynamic World new water;
- overlap SAR × Dynamic World;
- suprafață eliminată de masca JRC;
- clădiri potențial expuse;
- kilometri de drum intersectați;
- obiective critice expuse;
- durata procesării.

### Grafice

Generează local grafice simple și curate:

1. bar chart:
   - apă nouă SAR;
   - apă nouă Dynamic World;
   - overlap;

2. bar chart:
   - teren agricol;
   - vegetație;
   - zonă construită;

3. bar chart:
   - clădiri;
   - drumuri;
   - obiective critice;
   - căi ferate;

4. opțional:
   - evoluția temporală SAR dacă este calculată.

### Reguli raport

- folosește HTML semantic;
- folosește CSS local, fără dependențe externe obligatorii;
- graficul trebuie să fie integrat ca imagine base64 sau fișier local inclus;
- raportul trebuie să rămână lizibil offline;
- nu afișa dump-uri JSON lungi în corpul principal;
- mută detaliile tehnice în anexă;
- include nota metodologică:
  `Rezultatele reprezintă produse GEOINT preliminare de suport decizional și nu constituie confirmare oficială din teren.`
- include data generării;
- include sursele de date;
- include pragurile folosite;
- include limitările;
- include lista layerelor disponibile.

---

## 7. Exporturi

Păstrează:

```text
HTML
JSON
CSV
processing_log.txt
processing_log.json
```

Adaugă:

```text
charts/
report_assets/
```

Dacă OSM este disponibil, exportă și:

```text
osm_exposed_buildings.geojson
osm_intersected_roads.geojson
osm_critical_facilities.geojson
```

---

## 8. Teste

Adaugă teste pentru:

- catalog unic de stiluri;
- legendă contextuală;
- culori Dynamic World;
- categorii layer control;
- lazy loading;
- iconuri OSM și fallback;
- limbă UI coerentă;
- tooltip-uri pentru parametri;
- raport HTML;
- grafice;
- raport offline;
- raport fără OSM;
- raport fără Sentinel-2;
- raport fără EMS.

---

## 9. Verificare manuală

1. pornește aplicația;
2. verifică dacă UI-ul este integral în română;
3. deschide legenda;
4. verifică culorile pentru Dynamic World;
5. activează și dezactivează layer-ele;
6. verifică gruparea layerelor;
7. încarcă layer-ele suplimentare;
8. verifică simbolurile OSM;
9. generează raportul;
10. deschide raportul HTML offline;
11. verifică graficele;
12. verifică lizibilitatea raportului.

---

## 10. Restricții

- nu modifica algoritmii SAR în acest sprint;
- nu modifica pragurile implicite fără justificare;
- nu încărca toate layerele implicit;
- nu introduce dependențe externe obligatorii pentru raport;
- nu face push înainte de testare.

---

## La final

- rulează `pytest`;
- pornește aplicația;
- verifică vizual;
- afișează `git diff --stat`;
- rulează `/review`;
- oprește-te înainte de push.
