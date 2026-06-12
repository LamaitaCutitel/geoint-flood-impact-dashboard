# Sprint 1 — Stare și statusuri corecte

## Obiectiv
Elimină stările vechi și mesajele false de succes.

## Modificări
- În `reset_scene_selection()` golește:
  - `scene_candidates`;
  - `scene_query`;
  - `scene_errors`;
  - `scene_warnings`.
- La `Alege BEFORE` / `Alege AFTER` invalidează rezultatele dependente și PDF-ul.
- La schimbarea județului, AOI-ului sau scenelor:
  - dezactivează comparatoarele;
  - golește preview-urile;
  - golește raportul PDF.
- După orice retry OSM, Dynamic World manual sau rerulare SAR:
  - `state.report_bytes = None`;
  - `state.report_filename = ""`.
- Verifică rezultatul `execute_osm_loading()` în `execute_analysis()`.
- Separă statusurile:
  - SAR reușit;
  - OSM complet;
  - OSM parțial;
  - impact OSM indisponibil;
  - eroare.
- După rularea manuală Dynamic World, recalculează automat OSM × Dynamic World dacă `osm_impact` există.
- În modul detaliat păstrează activ implicit `dynamic_world_new_water`.

## Teste
- schimbare AOI golește galeria veche;
- alegere scenă nouă invalidează analiza;
- OSM eșuat nu produce mesaj verde;
- Dynamic World manual recalculează corelarea;
- PDF invalidat după recalculări.
