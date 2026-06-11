# Audit inițial — fără modificări

## Obiectiv

Inspectează codul existent și identifică ce module pot fi refolosite în tool-ul nou.

Nu modifica fișiere.

## Verifică

1. structura repository-ului;
2. pagina actuală Streamlit;
3. modulele de inițializare GEE;
4. selecția județelor;
5. desenarea AOI-ului, dacă există;
6. exploratorul temporal Sentinel-1;
7. sliderul BEFORE / AFTER existent;
8. funcțiile SAR water mask;
9. funcțiile Dynamic World;
10. modulele OSM din proiectul vechi sau cod reutilizabil;
11. registry-ul layerelor;
12. funcțiile de cache;
13. generarea raportului HTML / PDF, dacă există;
14. testele disponibile;
15. conflictele dintre controlul slider standard și controlul custom;
16. dependențele necesare pentru PDF și capturi ale hărții.

## Raportează

- module reutilizabile;
- module care trebuie izolate;
- funcții care trebuie rescrise;
- riscuri de regresie;
- dependențe lipsă;
- propunerea de structură pentru tool-ul nou;
- ordinea modificărilor.

## Restricții

- nu scrie cod;
- nu modifica fișiere;
- nu face commit;
- nu face push.
