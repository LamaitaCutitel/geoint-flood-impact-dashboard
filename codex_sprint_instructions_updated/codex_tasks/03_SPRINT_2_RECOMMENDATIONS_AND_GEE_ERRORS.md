# Sprint 2 — Recomandări SAR și erori GEE explicite

## Obiectiv

Repară recomandările automate BEFORE / AFTER și diferențiază lipsa scenelor de erorile tehnice.

## Partea A — Recomandări

Folosește `event_date` în toate apelurile.

Reguli:

- BEFORE recomandat = scenă validă anterioară evenimentului și cât mai apropiată;
- AFTER recomandat = scenă validă ulterioară evenimentului și cât mai apropiată;
- favorizează:
  1. aceeași polarizare;
  2. același instrument mode;
  3. aceeași direcție orbită;
  4. aceeași orbită relativă;
  5. acoperire AOI ridicată;
  6. distanță temporală minimă față de eveniment.

Elimină apelurile în care recomandările sunt calculate cu `event_date=None` dacă data este disponibilă.

## Partea B — Erori GEE

Înlocuiește returnarea simplă `[]` cu rezultat structurat:

```python
{
    "scenes": [],
    "warnings": [],
    "errors": [],
    "query_duration": 0,
    "query_parameters": {}
}
```

Diferențiază în UI:

- zero scene găsite;
- autentificare GEE lipsă;
- timeout;
- eroare query;
- AOI invalid;
- conexiune indisponibilă.

## Restricții

- nu modifica sliderul;
- nu modifica algoritmul final SAR;
- nu adăuga OSM;
- nu adăuga EMS.

## Teste

Adaugă teste pentru:

- BEFORE înainte de eveniment;
- AFTER după eveniment;
- aceeași orbită relativă favorizată;
- lipsă scene;
- eroare GEE simulată;
- mesaj UI diferit pentru eroare și zero rezultate.

## La final

- rulează `pytest`;
- afișează `git diff --stat`;
- rulează `/review`;
- nu face push;
- oprește-te.
