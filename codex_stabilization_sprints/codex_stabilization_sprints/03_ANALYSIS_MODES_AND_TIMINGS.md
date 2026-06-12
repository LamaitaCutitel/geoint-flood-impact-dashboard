# Sprint 3 — Moduri de analiză și cronometre

## Obiectiv
Reduce timpul de așteptare și separă analiza rapidă de cea completă.

## Modificări
Adaugă:

### Rapidă
- SAR BEFORE/AFTER;
- apă nouă SAR;
- clădiri afectate;
- drumuri principale;
- poduri;
- obiective critice;
- buffer;
- OSM din cache local;
- fără Dynamic World automat.

### Detaliată
- tot modul Rapid;
- Dynamic World;
- corelare multisursă;
- toate categoriile OSM;
- statistici complete;
- raport complet.

Adaugă:
- `Rulează analiza rapidă`;
- `Rulează analiza detaliată`;
- `Rulează / Reîncearcă Dynamic World`;
- cronometre pentru scene, thumbnails, SAR, vectorizare, cache OSM, impact OSM, Dynamic World, hartă și PDF.

## Teste
- Rapidă nu rulează Dynamic World;
- Detaliată rulează toate etapele;
- timpii apar în jurnal.
