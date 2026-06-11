# Sprint 3 — Strategie SAR hibridă

## Obiectiv

Separă metoda BEFORE de metoda AFTER.

## Default recomandat

```text
BEFORE = compozit median din scene compatibile
AFTER = scenă individuală selectată manual
```

## Implementare

Adaugă:

```text
Metodă BEFORE
- Scenă individuală
- Compozit median din scene compatibile

Metodă AFTER
- Scenă individuală selectată manual
- Compozit median pe interval scurt
- Minimum SAR / percentilă joasă exploratorie
```

Reguli:
- nu folosi median AFTER pe interval larg implicit;
- marchează produsul minimum/percentilă ca exploratoriu;
- salvează metodele în raport și legendă;
- păstrează sliderul temporal.

## Teste

Adaugă teste pentru:
- default BEFORE median;
- default AFTER individual;
- AFTER median scurt;
- produs exploratoriu etichetat;
- raport.

## La final

- rulează `pytest`;
- afișează `git diff --stat`;
- rulează `/review`;
- oprește-te înainte de commit.
