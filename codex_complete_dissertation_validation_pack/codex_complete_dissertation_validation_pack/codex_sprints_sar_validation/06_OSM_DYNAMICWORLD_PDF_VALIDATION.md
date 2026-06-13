# Sprint 6 — Verificarea produselor derivate

## Obiectiv
Validează rezultatele vizibile și raportul final.

## Modificări
- Afișează clar pentru fiecare produs:
  - disponibil;
  - indisponibil;
  - eroare;
  - sursă;
  - timp.
- Dynamic World:
  - verifică BEFORE/AFTER;
  - acoperire;
  - mozaic fallback;
  - suprapunere cu SAR.
- OSM:
  - verifică sursa cache/live;
  - completitudinea;
  - direct/buffer/context;
  - clădiri, drumuri, căi ferate, poduri, obiective critice.
- PDF:
  - generează;
  - salvează local;
  - verifică existența;
  - verifică numărul de pagini;
  - verifică nota obligatorie;
  - verifică structural tabelele și graficele.
- Păstrează verificarea vizuală manuală drept pas obligatoriu.

## Teste
- PDF există;
- nota obligatorie există;
- statusurile sunt lizibile;
- nu apar valori zero false;
- cache OSM complet/parțial raportat corect.
