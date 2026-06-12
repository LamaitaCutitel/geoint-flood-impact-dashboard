# Sprint 5 — Rezultate OSM vizibile și performanță

## Obiectiv
Afișează clar impactul OSM fără blocarea hărții.

## Modificări
- Păstrează datele brute pe disc.
- În state păstrează doar:
  - status;
  - metrici;
  - referințe cache;
  - subseturi afișabile.
- Reutilizează geometriile proiectate și `STRtree`.
- La schimbarea bufferului:
  - nu reproiecta tot;
  - recalculează doar intersecțiile.
- Pentru drumuri și căi ferate:
  - `direct_geometry`;
  - `buffer_geometry`;
  - `context_geometry`.
- Clădiri:
  - direct;
  - buffer;
  - referință max. `500 m`;
  - sortează referințele după distanță;
  - maximum `750`.
- Obiective critice:
  - un singur marker;
  - clustering;
  - iconuri reprezentative;
  - popup cu nume, categorie, status, distanță și sursă.
- Nu afișa toate clădirile din județ.

## Teste
- fără duplicate;
- segmente separate;
- referințe apropiate;
- schimbare buffer rapidă;
- markeri;
- popup-uri;
- randare hartă.
