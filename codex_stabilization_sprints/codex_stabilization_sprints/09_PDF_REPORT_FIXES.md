# Sprint 9 — Raport PDF

## Obiectiv
Corectează raportul și cache-ul PDF.

## Modificări
- PDF cache key = payload hash complet:
  analysis hash, buffer, OSM metadata, Dynamic World date, analysis mode, report version.
- Numele PDF folosește `event_date`; fallback la AFTER.
- Harta sintetică folosește `clipped_geometry` pentru linii.
- Include apă SAR, buffer, clădiri, drumuri, căi ferate, poduri, obiective, legendă, nord și scară.
- Calculează real OSM × Dynamic World: clasă BEFORE, clasă AFTER, tranziție, status direct/buffer.
- Grafice separate pentru număr elemente, lungimi km, suprafețe m² și Dynamic World.
- Include surse și data cache OSM.

## Teste
- PDF rapid și detaliat;
- cache PDF invalidat;
- clipped geometry;
- grafice omogene;
- diacritice;
- lipsă date.
