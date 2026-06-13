# Sprint 2 — Compatibilitatea scenelor și praguri SAR

## Obiectiv
Crește robustețea comparației BEFORE/AFTER și justificarea parametrilor.

## Modificări
- Pentru rularea finală implicită cere:
  - aceeași polarizare;
  - același `instrumentMode`;
  - același `orbit_pass`;
  - aceeași orbită relativă.
- Păstrează override pentru orbită relativă diferită numai în mod experimental:
  - checkbox explicit;
  - avertisment vizibil;
  - consemnare în PDF și export JSON.
- Păstrează avertismentul pentru acoperire sub 90%.
- Adaugă opțional prag minim recomandat pentru rularea finală: acoperire >= 95%, cu override explicit.
- Integrează modurile existente:
  - VH: conservator `-20`, echilibrat `-18`, sensibil `-16`;
  - VV: conservator `-17`, echilibrat `-15`, sensibil `-13`;
  - manual.
- La schimbarea polarizării actualizează recomandarea, fără a suprascrie o valoare manuală confirmată.
- Exportă scenele, compatibilitatea și override-urile.

## Teste
- orbită relativă diferită blocată implicit;
- override experimental funcțional;
- VH și VV au praguri recomandate diferite;
- acoperirea redusă produce avertisment.
