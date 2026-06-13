# Sprint 6 — Afișare OSM și performanță hartă

## Obiectiv
Păstrează harta clară și rapidă.

## Modificări
- Separă `analysis_features` de `display_features`.
- Harta afișează doar direct, buffer și context relevant.
- Clădiri:
  - direct;
  - buffer;
  - referință la max. `500 m` de clădirile afectate;
  - fallback la apa nouă dacă nu există clădiri afectate.
- Nu trimite toate clădirile către Folium.
- Referințe doar la zoom mare și cu limită de randare.
- Drumuri/căi ferate: segmente efectiv afectate și context discret.
- Obiective critice:
  - un singur marker;
  - `FeatureGroup`;
  - clustering;
  - iconuri SVG;
  - pod = linie + icon.
- Culori: direct roșu, buffer portocaliu, referință gri.

## Teste
- fără markeri dubli;
- referință 500 m;
- clustering;
- segmente afectate;
- performanță hartă.
