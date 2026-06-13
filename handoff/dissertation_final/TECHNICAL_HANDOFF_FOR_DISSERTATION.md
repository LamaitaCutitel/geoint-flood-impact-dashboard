# Technical Handoff for Dissertation

## 1.1. Informații generale

- **Denumire recomandată pentru lucrare:** „Aplicație GEOINT pentru evaluarea preliminară a impactului inundațiilor”
- **Scop:** evaluarea preliminară a extinderii apei observate automat prin SAR și identificarea elementelor OpenStreetMap potențial expuse, cu suport Dynamic World și raport PDF.
- **Entrypoint principal:** `impact_tool.py`
- **Branch final:** `review/dissertation-ready-local-run`
- **Commit auditat al aplicației:** `abe48fb2102ad90c2577f1b33e40d78ddd61ef2f`
- **Commit de publicare al pachetului:** consultați ultimul commit al branch-ului după publicarea fișierelor din `handoff/dissertation_final/`.
- **Data și ora rulării locale validate:** `2026-06-13 05:00:16 +03:00`
- **Sistem de operare:** Windows, validat prin scripturile PowerShell de pornire și test local.
- **Versiune Python:** `Python 3.12.7`
- **Comandă de pornire:** `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass; .\scripts\start_app.ps1`
- **Adresă locală:** `http://127.0.0.1:8501`

## 1.2. Funcționalități implementate și validate

Stările au următorul sens:

- **VALIDAT:** verificat prin rulare locală documentată sau CI;
- **PARȚIAL VALIDAT:** implementarea și testele structurale există, dar fluxul real complet în browser nu a fost executat cap-coadă;
- **NEVALIDAT TEHNIC:** rezultatul real nu a fost obținut și verificat manual.

| Nr. | Funcționalitate | Stare | Observații și limitări |
|---:|---|---|---|
| 1 | Selectarea județului | PARȚIAL VALIDAT | Implementată prin selectbox și click pe hartă; necesită verificare vizuală manuală. |
| 2 | Presetul pentru Galați | PARȚIAL VALIDAT | Implementat; cache-ul Galați a fost validat separat. |
| 3 | Desenarea AOI-ului | PARȚIAL VALIDAT | Implementată și acoperită structural; necesită verificare manuală în browser. |
| 4 | Analiza fără AOI pentru întregul județ | PARȚIAL VALIDAT | Flux implementat; analiza GEE reală pentru județul complet nu a fost rulată cap-coadă. |
| 5 | Căutarea scenelor Sentinel-1 | PARȚIAL VALIDAT | Implementată; necesită rulare GEE reală și selecție manuală. |
| 6 | Thumbnail-urile Sentinel-1 | PARȚIAL VALIDAT | Cache PNG local și TTL implementate; necesită verificare vizuală. |
| 7 | Selecția manuală a scenei BEFORE | PARȚIAL VALIDAT | Implementată; scena finală nu a fost aleasă. |
| 8 | Selecția manuală a scenei AFTER | PARȚIAL VALIDAT | Implementată; scena finală nu a fost aleasă. |
| 9 | Validarea compatibilității scenelor | PARȚIAL VALIDAT | Implementată; necesită verificare cu perechea finală. |
| 10 | Sliderul vertical BEFORE–AFTER | PARȚIAL VALIDAT | Implementat; necesită verificare manuală prin drag în browser. |
| 11 | Rularea analizei rapide | NEVALIDAT TEHNIC | Flux implementat; nu a fost executat complet cu scene reale confirmate. |
| 12 | Rularea analizei detaliate | NEVALIDAT TEHNIC | Flux implementat; nu a fost executat complet cu Dynamic World și OSM reale. |
| 13 | Detectarea apei BEFORE | NEVALIDAT TEHNIC | Rezultat real indisponibil. |
| 14 | Detectarea apei AFTER | NEVALIDAT TEHNIC | Rezultat real indisponibil. |
| 15 | Calculul apei nou apărute | NEVALIDAT TEHNIC | Metodologia este implementată: `AFTER − BEFORE`; valoarea reală lipsește. |
| 16 | Dynamic World BEFORE | NEVALIDAT TEHNIC | Implementat; rezultat real nevizualizat. |
| 17 | Dynamic World AFTER | NEVALIDAT TEHNIC | Implementat; rezultat real nevizualizat. |
| 18 | Modificarea clasei apă | NEVALIDAT TEHNIC | Implementată; valoarea reală lipsește. |
| 19 | Corelarea SAR–Dynamic World | NEVALIDAT TEHNIC | Implementată; rezultatul real lipsește. |
| 20 | Încărcarea datelor OSM | PARȚIAL VALIDAT | Cache-ul a fost pregătit și verificat; impactul real depinde de apa nouă vectorizată. |
| 21 | Cache-ul local OSM pentru Galați | VALIDAT | Scriptul local verifică `buildings`, `roads`, `railways`, `bridges`, `critical`, `critical_rapid`. |
| 22 | Intersecția directă cu apa nouă | PARȚIAL VALIDAT | Implementată structural; rezultatele reale lipsesc. |
| 23 | Bufferul configurabil | PARȚIAL VALIDAT | Interval implementat: `1–1000 m`, implicit `250 m`; necesită verificare vizuală. |
| 24 | Filtrarea clădirilor de referință | PARȚIAL VALIDAT | Implementată; maximum `750` elemente; necesită verificare pe rezultat real. |
| 25 | Simbolurile pentru obiective importante | PARȚIAL VALIDAT | Implementate; necesită verificare vizuală. |
| 26 | Tabelul cu elemente prioritare | PARȚIAL VALIDAT | Implementat; nu există date reale finale. |
| 27 | Modul prezentare | PARȚIAL VALIDAT | Implementat; necesită verificare vizuală. |
| 28 | Raportul PDF | PARȚIAL VALIDAT | Generatorul ReportLab și structura sunt testate; conținutul real nu a fost validat vizual. |
| 29 | Salvarea locală a raportului | PARȚIAL VALIDAT | Implementată în `data/output/reports/`; raportul final nu este versionat. |
| 30 | Funcția de download PDF | PARȚIAL VALIDAT | Implementată în UI; necesită verificare manuală în browser. |

## 1.3. Fluxul final al aplicației

Fluxul implementat este:

1. utilizatorul selectează județul;
2. utilizatorul poate desena opțional un AOI;
3. utilizatorul caută scene Sentinel-1;
4. aplicația afișează scenele și thumbnail-urile;
5. utilizatorul alege manual scena `BEFORE`;
6. utilizatorul alege manual scena `AFTER`;
7. utilizatorul compară imaginile prin separatorul vertical;
8. utilizatorul confirmă perechea;
9. utilizatorul setează pragul SAR și bufferul;
10. utilizatorul rulează analiza rapidă sau detaliată;
11. aplicația calculează `apă nouă SAR = apă AFTER − apă BEFORE`;
12. în modul detaliat, aplicația rulează Dynamic World;
13. aplicația încarcă și analizează elementele OSM după SAR;
14. aplicația afișează layerele, metricile și elementele potențial expuse;
15. aplicația generează raportul PDF.

## 1.4. Scene Sentinel-1 utilizate

| Parametru | BEFORE | AFTER |
|---|---|---|
| ID scenă Sentinel-1 | [DE COMPLETAT DUPĂ RULAREA FINALĂ] | [DE COMPLETAT DUPĂ RULAREA FINALĂ] |
| Data achiziției | [DE COMPLETAT DUPĂ RULAREA FINALĂ] | [DE COMPLETAT DUPĂ RULAREA FINALĂ] |
| Ora achiziției | [DE COMPLETAT DUPĂ RULAREA FINALĂ] | [DE COMPLETAT DUPĂ RULAREA FINALĂ] |
| Polarizare | [DE COMPLETAT DUPĂ RULAREA FINALĂ] | [DE COMPLETAT DUPĂ RULAREA FINALĂ] |
| Orbit pass | [DE COMPLETAT DUPĂ RULAREA FINALĂ] | [DE COMPLETAT DUPĂ RULAREA FINALĂ] |
| Orbită relativă | [DE COMPLETAT DUPĂ RULAREA FINALĂ] | [DE COMPLETAT DUPĂ RULAREA FINALĂ] |
| Acoperire AOI sau județ (%) | [DE COMPLETAT DUPĂ RULAREA FINALĂ] | [DE COMPLETAT DUPĂ RULAREA FINALĂ] |
| Tip produs | [DE COMPLETAT DUPĂ RULAREA FINALĂ] | [DE COMPLETAT DUPĂ RULAREA FINALĂ] |

- Aria utilizată: [DE COMPLETAT DUPĂ RULAREA FINALĂ]
- Suprafața ariei analizate: [DE COMPLETAT DUPĂ RULAREA FINALĂ]
- BBOX: [DE COMPLETAT DUPĂ RULAREA FINALĂ]
- Compatibilitate scene: [DE COMPLETAT DUPĂ RULAREA FINALĂ]
- Avertismente: [DE COMPLETAT DUPĂ RULAREA FINALĂ]

## 1.5. Parametrii SAR utilizați

| Parametru | Valoare utilizată |
|---|---:|
| Prag apă SAR, dB | [DE COMPLETAT DUPĂ RULAREA FINALĂ] |
| Smoothing, m | [DE COMPLETAT DUPĂ RULAREA FINALĂ] |
| Minimum connected pixels | [DE COMPLETAT DUPĂ RULAREA FINALĂ] |
| Scale, m | [DE COMPLETAT DUPĂ RULAREA FINALĂ] |
| Buffer OSM, m | [DE COMPLETAT DUPĂ RULAREA FINALĂ] |

Pragul SAR trebuie prezentat ca parametru ajustabil. Motivul alegerii și valorile testate trebuie completate numai după verificarea vizuală a rezultatelor reale.

## 1.6. Rezultate SAR

| Indicator | Valoare |
|---|---:|
| Suprafață apă BEFORE, km² | [DE COMPLETAT DUPĂ RULAREA FINALĂ] |
| Suprafață apă AFTER, km² | [DE COMPLETAT DUPĂ RULAREA FINALĂ] |
| Apă nouă evidențiată prin SAR, km² | [DE COMPLETAT DUPĂ RULAREA FINALĂ] |
| Durată procesare SAR, s | [DE COMPLETAT DUPĂ RULAREA FINALĂ] |
| Durată vectorizare, s | [DE COMPLETAT DUPĂ RULAREA FINALĂ] |

Valorile vor fi prezentate ca rezultate preliminare și necesită verificare în teren. Zonele suspecte de clasificare eronată trebuie descrise după analiza vizuală finală.

## 1.7. Rezultate Dynamic World

| Indicator | Valoare |
|---|---:|
| Data efectivă BEFORE | [DE COMPLETAT DUPĂ RULAREA FINALĂ] |
| Data efectivă AFTER | [DE COMPLETAT DUPĂ RULAREA FINALĂ] |
| Tip produs BEFORE | [DE COMPLETAT DUPĂ RULAREA FINALĂ] |
| Tip produs AFTER | [DE COMPLETAT DUPĂ RULAREA FINALĂ] |
| Acoperire BEFORE, % | [DE COMPLETAT DUPĂ RULAREA FINALĂ] |
| Acoperire AFTER, % | [DE COMPLETAT DUPĂ RULAREA FINALĂ] |
| Apă nouă Dynamic World, km² | [DE COMPLETAT DUPĂ RULAREA FINALĂ] |
| Suprapunere SAR × Dynamic World, km² | [DE COMPLETAT DUPĂ RULAREA FINALĂ] |
| Apă nouă doar SAR, km² | [DE COMPLETAT DUPĂ RULAREA FINALĂ] |
| Apă nouă doar Dynamic World, km² | [DE COMPLETAT DUPĂ RULAREA FINALĂ] |

Modificări observate pentru clasele `culturi`, `iarbă`, `construit`, `arbori`, `vegetație inundată`, `arbuști`, `teren gol`: [DE COMPLETAT DUPĂ RULAREA FINALĂ].

## 1.8. Rezultate OpenStreetMap

| Indicator | Valoare |
|---|---:|
| Clădiri intersectate direct | [DE COMPLETAT DUPĂ RULAREA FINALĂ] |
| Clădiri în buffer | [DE COMPLETAT DUPĂ RULAREA FINALĂ] |
| Clădiri de referință afișate | [DE COMPLETAT DUPĂ RULAREA FINALĂ] |
| Suprafață totală clădiri afectate, m² | [DE COMPLETAT DUPĂ RULAREA FINALĂ] |
| Suprapunere clădiri–apă, m² | [DE COMPLETAT DUPĂ RULAREA FINALĂ] |
| Clădiri complet intersectate | [DE COMPLETAT DUPĂ RULAREA FINALĂ] |
| Clădiri parțial intersectate | [DE COMPLETAT DUPĂ RULAREA FINALĂ] |
| Drumuri intersectate direct, km | [DE COMPLETAT DUPĂ RULAREA FINALĂ] |
| Drumuri în buffer, km | [DE COMPLETAT DUPĂ RULAREA FINALĂ] |
| Căi ferate intersectate direct, km | [DE COMPLETAT DUPĂ RULAREA FINALĂ] |
| Căi ferate în buffer, km | [DE COMPLETAT DUPĂ RULAREA FINALĂ] |
| Poduri intersectate direct | [DE COMPLETAT DUPĂ RULAREA FINALĂ] |
| Poduri în buffer | [DE COMPLETAT DUPĂ RULAREA FINALĂ] |
| Obiective critice intersectate direct | [DE COMPLETAT DUPĂ RULAREA FINALĂ] |
| Obiective critice în buffer | [DE COMPLETAT DUPĂ RULAREA FINALĂ] |

### Elemente critice prioritare

| Nr. | Nume | Categorie | Status | Distanță până la apă, m | Nivel infrastructură |
|---:|---|---|---|---:|---|
| 1 | [DE COMPLETAT DUPĂ RULAREA FINALĂ] | | | | |

- Sursa OSM finală: [DE COMPLETAT DUPĂ RULAREA FINALĂ]
- Data cache-ului: [DE COMPLETAT DUPĂ RULAREA FINALĂ]
- Completitudine: cache-ul local Galați a fost validat pentru categoriile scriptului; completitudinea rezultatului final trebuie confirmată după rularea analizei.
- Limitare: expunerea geometrică nu reprezintă automat o pagubă reală și necesită verificare în teren.

## 1.9. Timpi de execuție

| Etapă | Durată, s |
|---|---:|
| Inițializare | [DE COMPLETAT DUPĂ RULAREA FINALĂ] |
| Căutare scene | [DE COMPLETAT DUPĂ RULAREA FINALĂ] |
| Thumbnail-uri | [DE COMPLETAT DUPĂ RULAREA FINALĂ] |
| SAR | [DE COMPLETAT DUPĂ RULAREA FINALĂ] |
| Vectorizare | [DE COMPLETAT DUPĂ RULAREA FINALĂ] |
| Dynamic World | [DE COMPLETAT DUPĂ RULAREA FINALĂ] |
| Cache OSM | [DE COMPLETAT DUPĂ RULAREA FINALĂ] |
| Impact OSM | [DE COMPLETAT DUPĂ RULAREA FINALĂ] |
| Hartă | [DE COMPLETAT DUPĂ RULAREA FINALĂ] |
| PDF | [DE COMPLETAT DUPĂ RULAREA FINALĂ] |
| Total analiză | [DE COMPLETAT DUPĂ RULAREA FINALĂ] |

Timp validat separat pentru rularea locală automată de verificare: `35.66 s`. Acesta nu este timpul analizei GEE și nu trebuie prezentat drept timp de procesare a studiului de caz.

## 1.10. Raport PDF

- Nume fișier final: [DE COMPLETAT DUPĂ RULAREA FINALĂ]
- Locație locală implementată: `data/output/reports/`
- Număr de pagini: [NEVALIDAT TEHNIC]
- Harta sintetică lizibilă: [NEVALIDAT TEHNIC]
- Grafice lizibile: [NEVALIDAT TEHNIC]
- Tabele lizibile: [NEVALIDAT TEHNIC]
- Utilizare ca anexă: [NEVALIDAT TEHNIC]

Generatorul PDF este testat structural, însă raportul final cu rezultate reale nu este disponibil în repository și nu a fost validat vizual.

## 1.11. Limitări metodologice

- sensibilitatea SAR la geometria achiziției;
- sensibilitatea rezultatului la pragul ales;
- posibile erori de clasificare;
- dificultatea evidențierii vegetației inundate;
- efectele umbrei radar;
- influența rugozității suprafeței;
- decalajele temporale dintre produse;
- caracterul automat al Dynamic World;
- completitudinea variabilă a datelor OSM;
- diferența dintre expunerea geometrică și paguba reală;
- necesitatea verificării în teren.

## 1.12. Concluzie tehnică

1. **Aplicația poate fi prezentată în disertație?** Da, ca prototip funcțional și flux GEOINT preliminar validat structural.
2. **Fluxul complet Galați a fost validat?** Nu. [NEVALIDAT TEHNIC]
3. **Scenele selectate sunt adecvate?** [DE COMPLETAT DUPĂ RULAREA FINALĂ]
4. **Pragul SAR este acceptabil?** [DE COMPLETAT DUPĂ RULAREA FINALĂ]
5. **Rezultatele sunt plauzibile?** [DE COMPLETAT DUPĂ RULAREA FINALĂ]
6. **Ce rezultate pot fi incluse?** Arhitectura, metodologia, fluxul, funcțiile implementate, limitările și verificările automate.
7. **Ce rezultate trebuie prezentate cu precauție?** Orice metrică SAR, Dynamic World sau OSM obținută ulterior prin rularea reală.
8. **Ce rezultate nu trebuie incluse încă?** Valorile finale, scenele finale, capturile finale și concluziile privind terenul.
9. **Ce funcții sunt demonstrabile în prezent?** Pornirea aplicației, verificările automate, cache-ul Galați și structura UI; demonstrarea completă necesită rularea manuală în browser.
10. **Ce funcții trebuie îmbunătățite ulterior?** Validarea manuală cap-coadă, capturile, verificarea vizuală a PDF-ului și compararea cu observații din teren.
