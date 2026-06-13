# Sprint 2 — Comparator scene și stare

## Obiectiv
Separă clar comparația scenelor de comparația produselor analizate.

## Modificări
### Comparator scene
- înainte de analiză;
- buton `Compară imaginile`;
- folosește `SideBySideLayers`;
- drag direct pe bara verticală;
- fără slider orizontal;
- BEFORE stânga, AFTER dreapta;
- butoane:
  - `Compară imaginile`;
  - `Confirmă imaginile`;
  - `Ieși din comparație`;
  - `Curăță selecția`.

### Stare
- la schimbarea scenei:
  - invalidează analiza;
  - invalidează PDF-ul;
  - golește comparația veche;
  - marchează perechea neconfirmată.
- corectează ordinea din `apply_scene_pair()`:
  - resetare;
  - setare pereche;
  - `comparison_ready=True`.

### Comparator rezultate
- păstrează separat tool-ul Leaflet `↔`;
- nu permite două comparatoare active simultan;
- nu afișa bara dacă lipsesc tile URL-uri valide.

## Teste
- un singur divider;
- comparație înainte de confirmare;
- invalidare rezultate;
- invalidare PDF;
- comparator tematic separat.
