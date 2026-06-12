# Sprint 6 — Dynamic World și PDF

## Obiectiv
Păstrează analiza detaliată lizibilă și robustă.

## Modificări
- Dynamic World:
  - status vizibil;
  - acoperire;
  - dată efectivă;
  - tip produs;
  - mozaic fallback dacă acoperire `< 85%`;
  - tile errors vizibile;
  - layere BEFORE/AFTER/new water.
- Corelare:
  - SAR × Dynamic World;
  - OSM × Dynamic World.
- PDF:
  - invalidare la orice recalculare;
  - fără JSON brut;
  - tabele lizibile;
  - grafice separate pe unități;
  - scară reală;
  - legendă;
  - surse;
  - data cache OSM;
  - timpi;
  - limitări.

## Teste
- Dynamic World vizibil;
- fallback mozaic;
- tile error;
- PDF regenerat;
- fără JSON brut;
- diacritice.
