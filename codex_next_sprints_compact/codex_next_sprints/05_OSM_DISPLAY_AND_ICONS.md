# Sprint 5 — Afișare OSM și iconuri

## Obiectiv
Corectează simbolurile și păstrează harta lizibilă.

## Modificări
- Elimină afișarea dublă a obiectivelor.
- Folosește `FeatureGroup` controlabil.
- Iconuri reale sau SVG local: spital, clinică, farmacie, pompieri, poliție, școală, benzinărie, electric, gară, pod.
- Culoare după status: direct roșu, buffer portocaliu, referință gri.
- Poduri: linie + icon la centroid.
- Marker clustering.
- Clădiri afișate: direct, în buffer, referință la max. `500 m`.
- Nu trimite toate clădirile către Folium.
- Drumuri: segmente afectate și context relevant.

## Teste
Marker unic, iconuri, pod, clustering, clădiri referință, performanță hartă.
