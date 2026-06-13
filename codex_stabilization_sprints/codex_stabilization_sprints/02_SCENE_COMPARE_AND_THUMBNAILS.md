# Sprint 2 — Comparare scene și thumbnail-uri

## Obiectiv
Restaurează explorarea vizuală rapidă a imaginilor Sentinel-1.

## Modificări
- Adaugă deasupra `Confirmă imaginile` butonul `Compară imaginile`.
- Flux: `alege BEFORE/AFTER → compară → confirmă`.
- Comparatorul folosește bara verticală trasă direct cu mouse-ul.
- Elimină sliderul orizontal separat.
- Reutilizează controlul stabil din tool-ul vechi.
- Thumbnail-uri:
  - afișează metadatele imediat;
  - generează doar primele `6–8`;
  - buton `Afișează mai multe`;
  - cache local PNG + metadata + TTL;
  - regenerează automat thumbnail expirat sau lipsă.
- Comparatorul `Doar apă SAR` folosește aceiași parametri ca analiza finală.

## Teste
- buton comparare înainte de confirmare;
- drag direct pe bara verticală;
- fără slider orizontal;
- cache thumbnail hit/miss/expired.
