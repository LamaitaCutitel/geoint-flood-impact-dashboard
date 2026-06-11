# Checklist manual complet — înainte de OSM

## Pornire

- aplicația pornește fără pagină albă;
- harta este centrată pe România;
- basemap-ul color este vizibil;
- județele au numai contur;
- Galați poate fi selectat;
- click pe alt județ funcționează;
- zoom-ul funcționează.

## Stare sesiune

- după schimbarea județului dispar scenele vechi;
- după schimbarea perioadelor dispar selecțiile vechi;
- după schimbarea polarizării dispar selecțiile vechi;
- după schimbarea orbit pass dispar selecțiile vechi.

## Explorator SAR

- căutarea scenelor funcționează;
- zero rezultate este diferențiat de eroare GEE;
- timeline-ul afișează scenele;
- data și ora scenei sunt vizibile;
- recomandările BEFORE / AFTER sunt corecte;
- thumbnail-ul apare;
- preview grayscale apare;
- preview doar apă SAR apare.

## Slider candidat

- selectează BEFORE;
- selectează AFTER;
- apasă comparație;
- bara verticală apare;
- bara poate fi glisată;
- zoom-ul rămâne stabil;
- ieșirea din comparație funcționează;
- repornirea comparației funcționează.

## Analiză finală

- default BEFORE median;
- default AFTER individual;
- `SAR water BEFORE`;
- `SAR water AFTER`;
- `SAR new water`;
- `SAR flood extent filtrat`;
- `Dynamic World BEFORE`;
- `Dynamic World AFTER`;
- `Dynamic World new water`;
- overlap SAR × Dynamic World;
- masca JRC;
- indicatori;
- raport;
- legendă.

## Slider final

- apare fără duplicări;
- poate fi glisat;
- schimbarea perechii funcționează;
- ieșirea din comparație funcționează.

## Lazy loading

- analiza standard încarcă doar layer-ele esențiale;
- layer-ele suplimentare se încarcă la cerere;
- analiza principală nu este relansată.

## Git

- `pytest`;
- `/diff`;
- `/review`;
- `git status`;
- commit;
- push.
