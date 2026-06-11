# Sprint 3 — Strategie SAR hibridă

## Obiectiv

Separă metoda de construire a baseline-ului BEFORE de metoda AFTER.

## Cerință metodologică

Default recomandat:

```text
BEFORE = compozit median din scene compatibile
AFTER  = scenă individuală selectată manual
```

Motivație:

- mediana BEFORE reduce speckle și oferă un baseline stabil;
- mediana AFTER pe un interval larg poate dilua vârful inundației;
- scena AFTER trebuie să surprindă momentul cu extinderea vizibilă maximă a apei.

## Implementare

Înlocuiește opțiunea unică pentru compozit median cu două controale:

```text
Metodă BEFORE
- Scenă individuală
- Compozit median din scene compatibile

Metodă AFTER
- Scenă individuală selectată manual
- Compozit median pe interval scurt
- Minimum SAR / percentilă joasă exploratorie
```

Default:

```text
BEFORE = Compozit median din scene compatibile
AFTER = Scenă individuală selectată manual
```

## Reguli

- nu folosi automat compozit median AFTER pe interval larg;
- produsul `minimum SAR / percentilă joasă` trebuie marcat explicit `exploratoriu`;
- păstrează scenele manual selectate;
- păstrează sliderul temporal;
- salvează metoda folosită în raport și legendă.

## Restricții

- nu modifica OSM;
- nu adăuga EMS;
- nu schimba încă strategia Dynamic World.

## Teste

Adaugă teste pentru:

- default BEFORE median;
- default AFTER scenă individuală;
- AFTER median interval scurt;
- produs exploratoriu etichetat corect;
- raport cu metodele folosite.

## Verificare manuală

Compară:

1. BEFORE median + AFTER individual;
2. BEFORE individual + AFTER individual;
3. AFTER median interval scurt.

Verifică dacă produsul default păstrează mai bine extinderea maximă vizibilă.

## La final

- rulează `pytest`;
- afișează `git diff --stat`;
- rulează `/review`;
- nu face push;
- oprește-te.
