# Sprint 1 — Resetarea stării Streamlit

## Obiectiv

Elimină păstrarea datelor vechi după schimbarea AOI sau a parametrilor principali.

## Implementare

Creează:

```python
reset_county_dependent_state()
```

Apelează funcția:
- la click pe județ;
- la schimbarea județului din dropdown;
- la schimbarea intervalelor;
- la schimbarea polarizării;
- la schimbarea `orbit_pass`.

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

## Restricții

- nu modifica algoritmii SAR;
- nu modifica Dynamic World;
- nu adăuga OSM;
- nu adăuga EMS.

## Teste

Adaugă teste pentru:
- schimbare județ;
- schimbare perioadă;
- schimbare polarizare;
- schimbare orbit pass;
- eliminarea selecțiilor vechi.

## La final

- rulează `pytest`;
- afișează `git diff --stat`;
- rulează `/review`;
- oprește-te înainte de commit.
