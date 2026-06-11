# Sprint 5 — Dynamic World sincronizat și încărcare lazy

## Obiectiv

Crește relevanța Dynamic World și reduce timpul de încărcare.

## Partea A — Dynamic World AFTER

Adaugă două moduri:

```text
Dynamic World AFTER
- Interval complet
- Fereastră apropiată de scena SAR AFTER
```

Default:

```text
Fereastră apropiată de scena SAR AFTER
```

Reguli:

- folosește scena SAR AFTER selectată;
- fereastră configurabilă ±1–3 zile;
- fallback la interval complet dacă lipsesc date;
- salvează metoda și fereastra în raport;
- afișează perioada exactă în legendă.

## Partea B — Lazy loading

Generează imediat numai:

```text
SAR BEFORE
SAR AFTER
SAR water BEFORE
SAR water AFTER
SAR new water
SAR flood extent filtrat
Dynamic World BEFORE
Dynamic World AFTER
Dynamic World new water
SAR × Dynamic World overlap
JRC permanent water
```

Generează la cerere:

```text
SAR difference
SAR ratio
SAR persistent water
SAR water loss
Dynamic World other changes
RGB
NDWI
MNDWI
NDVI
NDMI
DEM
slope
hillshade
```

Adaugă buton:

```text
Încarcă layere suplimentare
```

Nu rerula analiza principală dacă utilizatorul cere numai tile-uri suplimentare.

## Indicatori

Afișează:

- apă nouă SAR;
- apă nouă Dynamic World;
- intersecție SAR × Dynamic World;
- procent overlap;
- suprafață eliminată de masca JRC.

## Restricții

- nu adăuga OSM;
- nu adăuga EMS.

## Teste

Adaugă teste pentru:

- fereastră Dynamic World;
- fallback interval complet;
- layer esențial;
- layer lazy;
- încărcare suplimentară fără rerularea analizei.

## Verificare manuală

1. rulează analiza standard;
2. măsoară timpul;
3. verifică layer-ele esențiale;
4. apasă `Încarcă layere suplimentare`;
5. verifică dacă analiza nu este relansată.

## La final

- rulează `pytest`;
- afișează `git diff --stat`;
- rulează `/review`;
- nu face push;
- oprește-te.
