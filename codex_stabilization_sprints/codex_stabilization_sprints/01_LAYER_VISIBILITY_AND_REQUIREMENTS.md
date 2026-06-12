# Sprint 1 — Vizibilitate layere și dependențe

## Obiectiv
Repară bugurile care împiedică afișarea layerelor și pornirea curată a aplicației.

## Modificări
- În `add_tile_layers()`, un layer deja filtrat ca activ trebuie randat cu `show=True`.
- Folosește `shown` doar pentru activarea implicită inițială.
- Verifică SAR BEFORE/AFTER, SAR new water, toate layerele Dynamic World și corelările.
- Afișează avertisment dacă `tile_url` lipsește.
- Completează `requirements.txt` cu `shapely`, `pyproj`, `matplotlib`, `reportlab`.

## Teste
- layer activ cu `shown=False` devine vizibil;
- layer fără `tile_url` produce warning;
- import curat într-un mediu nou.
