# Sprint 5 — Analiză SAR strict BEFORE / AFTER

## Obiectiv

Implementează analiza SAR simplă și transparentă.

## Regula metodologică

Nu folosi JRC.
Nu folosi mediană.
Nu folosi produse experimentale.

Calculează strict:

```text
Apă observată BEFORE
Apă observată AFTER
Apă nouă SAR = AFTER minus BEFORE
```

## Parametri

Păstrează numai parametrii necesari:
- polarizare;
- prag apă SAR;
- smoothing opțional;
- minimum connected pixels.

Pune parametrii avansați într-un expander.

## Layer-e SAR vizibile

```text
Apă observată BEFORE
Apă observată AFTER
Apă nouă evidențiată prin SAR
```

## Statistici

- suprafață apă BEFORE;
- suprafață apă AFTER;
- suprafață apă nouă;
- durată procesare.

## Reguli

- crop după AOI activ;
- selfMask pentru transparență;
- elimină pixeli izolați;
- nu afișa ratio;
- nu afișa difference tehnic;
- nu afișa DEM;
- nu afișa indici optici.

## Teste

- apă BEFORE;
- apă AFTER;
- new water;
- AOI crop;
- connected pixels;
- smoothing;
- suprafețe;
- fără JRC;
- fără layere tehnice în registry-ul tool-ului nou.

## La final

- rulează testele;
- verifică layer-ele;
- afișează `git diff --stat`;
- rulează `/review`;
- oprește-te înainte de commit.
