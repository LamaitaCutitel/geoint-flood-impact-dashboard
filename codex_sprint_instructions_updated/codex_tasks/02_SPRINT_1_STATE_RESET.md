# Sprint 1 — Resetarea sigură a stării Streamlit

## Obiectiv

Elimină riscul păstrării scenelor și rezultatelor unui județ anterior după schimbarea AOI.

## Implementare

Creează o funcție centrală:

```python
reset_county_dependent_state()
```

Folosește funcția:

- la schimbarea județului prin click;
- la schimbarea județului din dropdown;
- când se schimbă intervalele temporale;
- când se schimbă polarizarea;
- când se schimbă `orbit_pass`.

Resetează:

```text
sar_scene_results
sar_before_scene
sar_after_scene
sar_pair_status
sar_pair_confirmed
sar_candidate_compare
sar_preview
confirm_relative_orbit_mismatch
last_analysis_result
```

Păstrează cache-ul reutilizabil dacă parametrii nu se schimbă.

## Restricții

- nu modifica algoritmii SAR;
- nu modifica Dynamic World;
- nu adăuga OSM;
- nu adăuga EMS.

## Teste

Adaugă teste pentru:

- schimbare județ prin dropdown;
- schimbare județ prin click;
- schimbare perioadă;
- schimbare polarizare;
- schimbare orbit pass;
- eliminarea selecțiilor vechi.

## Verificare manuală

1. selectează Galați;
2. caută scene;
3. alege BEFORE și AFTER;
4. schimbă județul;
5. verifică dacă scenele, preview-ul și rezultatele vechi dispar.

## La final

- rulează `pytest`;
- afișează `git diff --stat`;
- rulează `/review`;
- nu face push;
- oprește-te.
