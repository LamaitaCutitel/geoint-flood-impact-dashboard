# Probleme si verificari ramase

## Necesita verificare manuala

- `[NEVALIDAT TEHNIC]` Capturile PNG 01-12 nu au putut fi produse de
  mecanismul browserului: captura paginii Streamlit cu harta Leaflet a expirat
  repetat la rezolutia obligatorie 1440 x 900.
- Verifica vizual fiecare layer SAR, Dynamic World si OSM in browser.
- Verifica vizual toate cele 7 pagini ale PDF-ului.
- Confirma interpretarea metodologica a valorilor SAR si Dynamic World.
- Decide forma finala a tabelelor si numarul de zecimale din disertatie.

## Limitari tehnice observate

- Rularea rapida cu OSM a depasit 10 minute si ramane
  `[NEVALIDAT TEHNIC]`.
- Rularea rapida fara OSM a reusit in aproximativ 34 secunde.
- Vectorizarea la 10 m a depasit 15 minute; configuratia finala foloseste
  vectorizare la 30 m si analiza raster la 10 m.
- Directorul temporar global pytest are permisiuni Windows defecte; testele
  sunt rulate cu un director temporar local.

## Checklist capturi

- `01_interfata_initiala.png` - `[NEVALIDAT TEHNIC]`
- `02_preset_galati.png` - `[NEVALIDAT TEHNIC]`
- `03_selectare_scene_sentinel1.png` - `[NEVALIDAT TEHNIC]`
- `04_slider_before_after.png` - `[NEVALIDAT TEHNIC]`
- `05_parametri_sar.png` - `[NEVALIDAT TEHNIC]`
- `06_rezultat_sar.png` - `[NEVALIDAT TEHNIC]`
- `07_dynamic_world.png` - `[NEVALIDAT TEHNIC]`
- `08_corelare_sar_dynamic_world.png` - `[NEVALIDAT TEHNIC]`
- `09_osm_impact.png` - `[NEVALIDAT TEHNIC]`
- `10_osm_elemente_prioritare.png` - `[NEVALIDAT TEHNIC]`
- `11_raport_pdf_coperta.png` - `[NEVALIDAT TEHNIC]`
- `12_raport_pdf_harta.png` - `[NEVALIDAT TEHNIC]`

Nu au fost create imagini substitut sau capturi artificiale.
