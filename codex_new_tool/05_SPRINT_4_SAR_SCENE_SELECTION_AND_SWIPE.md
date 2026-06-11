# Sprint 4 — Selecție scene Sentinel-1 și slider BEFORE / AFTER

## Obiectiv

Permite utilizatorului să aleagă exact două scene Sentinel-1 și să le compare vizual.

## Input

- județ / AOI activ;
- interval de căutare;
- polarizare;
- orbit pass.

## Rezultate căutare

Pentru fiecare scenă:
- ID;
- data și ora;
- polarizare;
- orbit pass;
- orbită relativă;
- procent acoperire AOI;
- thumbnail;
- warning-uri.

## UI

Două selecții:
```text
Imagine de referință (BEFORE)
Imagine după eveniment (AFTER)
```

Afișează:
- tabel interactiv;
- thumbnails;
- metadate;
- warning-uri;
- buton `Confirmă imaginile`.

## Slider obligatoriu

Adaugă swipe vertical:

```text
SAR BEFORE ↔ SAR AFTER
```

Moduri:
```text
Radar brut în tonuri de gri
Doar apă observată prin SAR
```

## Reguli

- un singur control swipe activ;
- fără controale duplicate;
- schimbarea scenei actualizează preview-ul;
- nu rulează analiza finală automat;
- păstrează zoom-ul;
- fallback dacă pluginul nu se încarcă;
- butonul de analiză rămâne blocat până la confirmare.

## Teste

- căutare scene;
- zero scene;
- eroare GEE;
- selecție BEFORE;
- selecție AFTER;
- confirmare;
- swipe;
- schimbare mod preview;
- lipsă plugin;
- scene incompatibile.

## La final

- rulează testele;
- verifică sliderul manual;
- afișează `git diff --stat`;
- rulează `/review`;
- oprește-te înainte de commit.
