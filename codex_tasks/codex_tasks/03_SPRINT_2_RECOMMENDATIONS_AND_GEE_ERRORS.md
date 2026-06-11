# Sprint 2 — Recomandări SAR și erori GEE

## Obiectiv

Repară recomandările automate și diferențiază zero rezultate de erori tehnice.

## Recomandări

Folosește `event_date` peste tot.

Reguli:
- BEFORE = scenă validă anterioară evenimentului și cât mai apropiată;
- AFTER = scenă validă ulterioară evenimentului și cât mai apropiată;
- favorizează aceeași polarizare, mode, pass, orbită relativă și acoperire AOI.

## Erori GEE

Returnează:
```python
{
  "scenes": [],
  "warnings": [],
  "errors": [],
  "query_duration": 0,
  "query_parameters": {}
}
```

Diferențiază:
- zero scene;
- autentificare lipsă;
- timeout;
- query invalid;
- AOI invalid;
- conexiune.

## Restricții

- nu modifica sliderul;
- nu modifica algoritmul final;
- nu adăuga OSM;
- nu adăuga EMS.

## La final

- rulează `pytest`;
- afișează `git diff --stat`;
- rulează `/review`;
- oprește-te înainte de commit.
