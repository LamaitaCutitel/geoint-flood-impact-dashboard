# Texte gata de inserat în disertație

## 1. Descrierea aplicației — text validat

În cadrul studiului de caz a fost dezvoltată o aplicație GEOINT pentru evaluarea preliminară a impactului inundațiilor. Aplicația integrează date Sentinel-1 SAR, produse Dynamic World și elemente OpenStreetMap într-un flux unic de analiză. Scopul instrumentului este sprijinirea interpretării rapide a extinderii apei observate automat și identificarea elementelor potențial expuse. Rezultatele generate au caracter preliminar și necesită verificare în teren.

## 2. Arhitectura aplicației — text validat

Aplicația este organizată modular. Componenta principală de interfață este implementată în Streamlit, iar harta interactivă utilizează Folium și Leaflet. Modulele dedicate analizei SAR, procesării Dynamic World, încărcării datelor OpenStreetMap, clasificării impactului geometric și generării raportului PDF sunt separate. Integrarea cu Google Earth Engine este utilizată pentru procesarea datelor satelitare, în timp ce datele OSM sunt stocate într-un cache local pentru reducerea timpului de răspuns.

## 3. Fluxul de utilizare — text validat

Utilizatorul selectează județul analizat și poate desena opțional o zonă de interes. În lipsa unei zone desenate manual, analiza se realizează la nivelul întregului județ. Ulterior, aplicația caută scene Sentinel-1 disponibile, afișează thumbnail-uri și permite selectarea manuală a unei scene BEFORE și a unei scene AFTER. Perechea poate fi inspectată vizual prin intermediul unui separator vertical înainte de confirmare. După confirmarea scenelor, utilizatorul configurează parametrii SAR și bufferul de avertizare, apoi rulează analiza rapidă sau detaliată.

## 4. Analiza SAR — text validat

Metodologia principală utilizează două scene Sentinel-1 individuale. Scena BEFORE caracterizează situația anterioară evenimentului, iar scena AFTER surprinde situația ulterioară. Apa nouă evidențiată prin SAR este calculată prin eliminarea zonelor de apă identificate anterior din zonele de apă observate după eveniment:

```text
apă nouă SAR = apă AFTER − apă BEFORE
```

Rezultatul trebuie interpretat ca extindere preliminară a apei observate automat prin SAR. Clasificarea poate fi influențată de geometria achiziției, rugozitatea suprafeței, pragul selectat, umbra radar și prezența vegetației inundate.

## 5. Dynamic World — text validat

În modul detaliat, aplicația utilizează produse Dynamic World pentru completarea interpretării rezultatului SAR. Sunt analizate observațiile BEFORE și AFTER, diferențele observate și modificarea clasei apă. În cazul în care observația individuală nu asigură o acoperire suficientă a ariei analizate, aplicația poate utiliza un mozaic fallback. Corelarea multisursă permite diferențierea zonelor evidențiate prin ambele metode de zonele identificate numai prin una dintre surse.

## 6. Analiza OpenStreetMap — text validat

După calcularea apei nou evidențiate, aplicația analizează elementele OpenStreetMap. Sunt evaluate clădirile, drumurile, căile ferate, podurile și obiectivele critice. Clasificarea face diferența între elementele intersectate geometric cu apa nouă, elementele aflate în bufferul de avertizare și elementele de context. Această clasificare indică expunerea potențială, nu paguba reală. Elementele identificate necesită verificare în teren.

## 7. Cache-ul local — text validat

Pentru reducerea timpului de răspuns, aplicația utilizează un cache local OpenStreetMap. Pentru județul Galați, scriptul de pregătire verifică datele aferente ariei județului extinse cu 1000 m. Sunt validate categoriile `buildings`, `roads`, `railways`, `bridges`, `critical` și `critical_rapid`. În lipsa cache-ului local, aplicația poate interoga Overpass API, însă timpul de răspuns poate varia.

## 8. Raportul PDF — text validat structural

Aplicația include un modul de generare locală a raportului PDF. Raportul centralizează aria analizată, perechea de scene Sentinel-1, parametrii, indicatorii SAR, statusul Dynamic World, impactul OSM, completitudinea datelor, harta sintetică, graficele, limitările și sursele. Documentul include explicit mențiunea că rezultatele reprezintă produse GEOINT preliminare de suport decizional și nu constituie confirmare oficială din teren.

## 9. Rezultatele studiului de caz — text provizoriu

Pentru studiul de caz aferent județului Galați au fost selectate scenele Sentinel-1 [DE COMPLETAT DUPĂ RULAREA FINALĂ] și [DE COMPLETAT DUPĂ RULAREA FINALĂ]. Analiza s-a realizat pentru [DE COMPLETAT DUPĂ RULAREA FINALĂ]. Suprafața apei nou evidențiate prin SAR a fost de [DE COMPLETAT DUPĂ RULAREA FINALĂ] km². Rezultatele Dynamic World au evidențiat [DE COMPLETAT DUPĂ RULAREA FINALĂ]. În urma intersecției geometrice cu elementele OSM au fost identificate [DE COMPLETAT DUPĂ RULAREA FINALĂ] clădiri și [DE COMPLETAT DUPĂ RULAREA FINALĂ] km de drumuri potențial expuse.

Acest paragraf nu trebuie inclus în forma finală înaintea validării manuale a fluxului Galați.

## 10. Limitările studiului de caz — text validat

Rezultatele trebuie interpretate cu precauție. Analiza SAR este sensibilă la geometria achiziției, pragul utilizat și caracteristicile suprafeței. Zonele cu vegetație inundată, umbră radar sau rugozitate redusă pot produce clasificări incerte. Produsele Dynamic World sunt obținute prin clasificare automată și pot exista decalaje temporale față de scenele SAR. Completitudinea elementelor OSM poate varia spațial. Intersecția geometrică indică expunerea potențială și nu reprezintă o confirmare a producerii unei pagube.

## 11. Concluziile studiului de caz — text provizoriu

Aplicația dezvoltată demonstrează posibilitatea integrării datelor Sentinel-1 SAR, Dynamic World și OpenStreetMap într-un flux GEOINT orientat către evaluarea preliminară a impactului unei inundații. [DE COMPLETAT DUPĂ RULAREA FINALĂ: interpretarea rezultatelor Galați]. Rezultatele pot sprijini prioritizarea verificărilor și intervențiilor, dar necesită validare în teren și corelare cu date suplimentare.
