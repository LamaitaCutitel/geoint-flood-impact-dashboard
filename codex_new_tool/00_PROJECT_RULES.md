# Reguli permanente pentru tool-ul nou

## Obiectiv

Acest fișier trebuie citit înainte de orice sprint.

## Repository

Lucrează în repository-ul existent:

```text
geoint-flood-impact-dashboard
```

Creează un tool nou, separat logic de dashboard-ul experimental existent.

Nu recrea repository-ul.
Nu elimina funcționalități vechi decât dacă produc conflicte directe.
Nu modifica `.env`.
Nu urca token-uri, chei, cache sau fișiere raster mari în Git.

## Scop

Tool-ul nou trebuie să fie orientat strict spre:

```text
Evaluarea impactului unei inundații
Analiză multisursă SAR, Dynamic World și OpenStreetMap
```

## Reguli metodologice

- fără JRC;
- analiză SAR strict BEFORE / AFTER;
- exact două scene Sentinel-1 selectate;
- rezultat principal SAR:
  - apă observată BEFORE;
  - apă observată AFTER;
  - apă nouă SAR;
- Dynamic World:
  - BEFORE;
  - AFTER;
  - modificări;
  - apă nouă Dynamic World;
- corelare:
  - apă nouă doar SAR;
  - apă nouă doar Dynamic World;
  - apă nouă prin ambele metode;
- OSM se încarcă numai după analiza SAR;
- impactul OSM se calculează pe baza apei noi SAR și a bufferului;
- AOI opțional, cu fallback la județ complet;
- buffer 1–1000 m;
- raport final PDF;
- fără ZIP.

## Reguli UI

- limba interfeței: română;
- harta este elementul central;
- layere puține și grupate;
- legenda explică doar layer-ele active;
- slider BEFORE / AFTER obligatoriu;
- simboluri OSM diferențiate;
- modul `Afișează doar impactul critic`;
- raport PDF disponibil printr-un singur buton principal.

## Formulări permise

Folosește:

```text
apă nouă evidențiată prin SAR
diferențe observate Dynamic World
element potențial expus
intersectat geometric
zonă în buffer de avertizare
necesită verificare în teren
```

Evită:

```text
inundație confirmată
clădire afectată cert
drum impracticabil
obiectiv distrus
```

## Reguli de testare

După fiecare sprint:
- rulează testele;
- pornește aplicația;
- verifică vizual;
- rulează `/diff`;
- rulează `/review`;
- oprește-te înainte de push.
