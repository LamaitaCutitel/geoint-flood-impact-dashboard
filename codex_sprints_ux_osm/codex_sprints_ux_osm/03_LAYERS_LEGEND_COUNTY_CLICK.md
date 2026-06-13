# Sprint 3 — Layere, legendă și click pe județ

## Obiectiv
Fă harta coerentă și ușor de controlat.

## Modificări
- LayerControl: doar:
  - `OSM Light / CartoDB Positron`;
  - `Satelit / Esri World Imagery`.
- Toate layerele tematice rămân în coloana din dreapta.
- Mută filtrele OSM înainte de construirea hărții sau folosește `st.rerun()` imediat.
- Construiește legenda din layerele active efectiv.
- Explică:
  - apă SAR;
  - apă Dynamic World;
  - buffer;
  - clădiri direct/buffer/referință;
  - drumuri direct/buffer;
  - căi ferate;
  - poduri;
  - obiective critice.
- Reintrodu click pe județ:
  - selectare;
  - zoom;
  - contur fără umplere;
  - resetare stare dependentă.

## Teste
- numai două basemap-uri;
- legendă actualizată;
- filtre aplicate imediat;
- click județ;
- zoom județ.
