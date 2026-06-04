# AGENTS

Reguli pentru sesiuni Codex viitoare:

- Pastreaza proiectul simplu si demonstrabil.
- Nu recrea proiectul de la zero.
- Nu adauga functii mari fara solicitare explicita.
- Nu hardcoda secrete, chei API, token-uri sau ID-uri private.
- Nu modifica `.env`.
- Nu urca token-uri sau chei.
- Pastreaza procesarea raster in Google Earth Engine.
- Nu procesa rastere mari local.
- Nu descarca automat rastere mari.
- Nu descarca automat GeoTIFF-uri.
- Ruleaza testele dupa modificari.
- Ruleaza `pytest` dupa fiecare sprint.
- Actualizeaza documentatia cand schimbi comportamentul.
- Pastreaza o singura harta interactiva pentru selectie si rezultate.
- Pastreaza functionalitatea de comparatie in harta, fara dropdown-uri Streamlit pentru layer stanga/dreapta.
- Clip-uieste rasterele dupa geometria judetului, nu doar dupa bounding box.
- Aplica crop dupa geometria exacta a judetului.
- Nu adauga OSM inainte de stabilizarea rasterului.
- Nu adauga EMS inainte de stabilizare si OSM.
- Nu introduce integrare ANAR in prima versiune.
- Nu introduce modele hidraulice sau predictii de precipitatii.
- Inainte de commit ruleaza `/diff`, `/review` si `git status`.
- Foloseste formulari prudente: `apa observata automat prin SAR`, `extindere preliminara`, `diferente observate Dynamic World`.
- Evita formularea `inundatie confirmata`.
