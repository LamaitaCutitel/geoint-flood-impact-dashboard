# Sprint 6 — Impact operațional OSM

## Precondiție

Nu începe acest sprint dacă fluxul raster nu este stabil și checklist-ul manual nu este trecut.

## Obiectiv

Adaugă impact operațional pe baza extinderii preliminare detectate.

## Ordine de implementare

1. clădiri;
2. drumuri;
3. obiective critice;
4. căi ferate;
5. poduri.

## Reguli de performanță

- nu încărca toate datele OSM pentru întreg județul;
- folosește bbox-ul extinderii detectate;
- aplică buffer configurabil;
- cache-uiește răspunsurile;
- limitează query-ul;
- nu vectoriza rasterul complet la rezoluție maximă în modul exploratoriu.

## Indicatori

- număr clădiri potențial afectate;
- kilometri de drum intersectați;
- obiective critice expuse;
- kilometri cale ferată intersectați;
- număr poduri intersectate.

## Layere

- clădiri expuse;
- drumuri intersectate;
- obiective critice;
- căi ferate;
- poduri.

## Formulare prudentă

Folosește:

- `potențial afectat`;
- `intersectat cu extinderea preliminară`;
- `expunere estimată`.

Nu folosi:

- `distrus`;
- `inaccesibil confirmat`;
- `afectat cert`.

## Restricții

- nu implementa încă validarea EMS;
- nu adăuga scor general 0–100.

## Teste

Adaugă teste pentru:

- bbox + buffer;
- cache;
- statistici clădiri;
- lungime drumuri;
- obiective critice;
- fallback Overpass/API indisponibil.

## La final

- rulează `pytest`;
- verifică vizual;
- afișează `git diff --stat`;
- rulează `/review`;
- nu face push;
- oprește-te.
