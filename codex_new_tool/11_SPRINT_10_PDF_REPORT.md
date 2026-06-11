# Sprint 10 — Raport PDF profesional

## Obiectiv

Generează un raport PDF detaliat, potrivit pentru prezentarea în fața comisiei.

## Buton unic principal

```text
Generează și descarcă raportul PDF
```

Nu genera ZIP.

## Nume fișier

```text
raport_geoint_inundatie_<judet>_<data_eveniment>.pdf
```

## Structură PDF

1. Copertă
2. Rezumat executiv
3. Județ și AOI
4. Buffer utilizat
5. Scene Sentinel-1 BEFORE / AFTER
6. Metodologia SAR
7. Rezultatele SAR
8. Dynamic World
9. Corelare SAR × Dynamic World
10. Impact OSM
11. Analiza OSM × Dynamic World
12. Grafice
13. Tabele detaliate
14. Limitări
15. Surse
16. Anexă tehnică
17. Durata procesării
18. Informații cache

## Imagine principală

Include o singură imagine reprezentativă:

```text
Harta sintetică a impactului inundației
```

Trebuie să arate:
- apă nouă SAR;
- buffer transparent;
- clădiri potențial expuse;
- drumuri;
- căi ferate;
- poduri;
- obiective critice cu simboluri.

Nu încărca PDF-ul cu multe capturi de hartă.

## Grafice

### Grafic 1 — Suprafețe de apă
- apă nouă SAR;
- apă nouă Dynamic World;
- suprapunere multisursă.

### Grafic 2 — Tranziții Dynamic World către apă
- culturi;
- iarbă;
- built;
- arbori;
- flooded vegetation.

### Grafic 3 — Elemente OSM
- clădiri;
- poduri;
- obiective critice.

### Grafic 4 — Infrastructură liniară
- drumuri;
- căi ferate.

### Grafic 5 — Direct vs buffer
- intersectat direct;
- în buffer.

## Tabele

- scene Sentinel-1;
- suprafețe SAR;
- suprafețe Dynamic World;
- corelare;
- clădiri;
- drumuri;
- căi ferate;
- poduri;
- obiective critice;
- tranziții Dynamic World;
- OSM × Dynamic World;
- parametri.

## Note obligatorii

Include:
```text
Rezultatele reprezintă produse GEOINT preliminare de suport decizional și nu constituie confirmare oficială din teren.
```

Include:
- lipsa JRC;
- limitări SAR;
- clasificare automată Dynamic World;
- completitudine variabilă OSM;
- decalaje temporale;
- necesitatea verificării în teren.

## Tehnic

- generează HTML intern dacă este util;
- convertește la PDF;
- PDF lizibil offline;
- CSS local;
- fonturi standard;
- grafice integrate;
- hartă integrată;
- fără dependențe externe obligatorii;
- cache pentru PDF.

## Teste

- PDF generat;
- PDF fără OSM complet;
- PDF fără Dynamic World;
- PDF cu AOI;
- PDF fără AOI;
- PDF buffer 1;
- PDF buffer 1000;
- imagine principală;
- grafice;
- tabele;
- limitări;
- cache raport.

## La final

- rulează testele;
- generează un PDF de probă;
- deschide-l și verifică layout-ul;
- afișează `git diff --stat`;
- rulează `/review`;
- oprește-te înainte de commit.
