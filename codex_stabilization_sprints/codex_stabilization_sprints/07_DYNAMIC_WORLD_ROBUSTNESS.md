# Sprint 7 — Dynamic World robust

## Obiectiv
Repară afișarea și diagnosticul Dynamic World.

## Modificări
- Status vizibil: reușit, indisponibil, eroare, tile indisponibil.
- Activează implicit doar `Apă nouă evidențiată prin Dynamic World`.
- Nu transforma erorile în `None` sau `0` fără explicație.
- Pentru fiecare tile: URL, status, error.
- Pentru metrici: value, status, error.
- Alege observația după acoperire AOI, proximitate temporală și pixeli valizi.
- Fallback mozaic dacă este necesar.
- Afișează perioada de căutare, data efectivă și tipul produsului.
- Grupează metricile într-un singur apel GEE dacă este posibil.

## Teste
- Dynamic World vizibil;
- tile error vizibil;
- zero real vs eroare;
- fallback mozaic;
- dată efectivă afișată.
