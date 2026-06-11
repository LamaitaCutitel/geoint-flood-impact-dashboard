# Sprint 2 — Județ, AOI și stare Streamlit

## Obiectiv

Implementează aria activă și resetarea corectă a stării.

## Regula AOI

Dacă utilizatorul nu desenează AOI:

```text
aria activă = județul complet
```

Dacă utilizatorul desenează AOI:

```text
aria activă = poligonul AOI
```

## UI

Afișează:

```text
Aria activă:
○ Județ complet
● Zonă focală desenată manual
```

Butoane:
- `Desenează zonă focală`;
- `Șterge AOI și revino la județ`.

## Reguli tehnice

- crop după geometria exactă;
- bbox doar pentru zoom și optimizare;
- calculează:
  - centroid;
  - bbox;
  - suprafață AOI;
  - hash AOI;
- validează AOI:
  - geometrie validă;
  - AOI în interiorul județului sau intersecție controlată;
  - avertizare dacă AOI este foarte mare;
  - avertizare dacă AOI este gol.

## State reset

Creează funcții centrale:

```python
reset_area_dependent_state()
reset_analysis_results()
reset_scene_selection()
```

La schimbarea județului sau AOI:
- șterge scenele selectate;
- șterge rezultatele analizei;
- șterge layerele rezultate;
- păstrează cache-ul reutilizabil.

## Teste

- județ fără AOI;
- județ cu AOI;
- ștergere AOI;
- AOI invalid;
- AOI gol;
- schimbare județ;
- reset selectiv al stării.

## La final

- rulează testele;
- verifică manual desenarea AOI;
- afișează `git diff --stat`;
- rulează `/review`;
- oprește-te înainte de commit.
