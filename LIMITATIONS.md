# LIMITATIONS

Aplicatia produce o extindere preliminara detectata automat prin SAR, nu o confirmare
oficiala a inundatiei.

Limitari principale:

- Observatia SAR poate diferi de situatia din teren.
- Momentul achizitiei Sentinel-1 poate rata maximul evenimentului.
- Pragurile SAR influenteaza sensibil rezultatul.
- Zgomotul radar si speckle pot produce false pozitive sau false negative.
- Vegetatia si suprafetele umede pot complica interpretarea.
- Dynamic World are rezolutie si incertitudini proprii.
- Nu exista validare oficiala in aceasta versiune.
- Aplicatia nu ruleaza modelare hidraulica si nu prezice precipitatii.
- Selectarea prin click direct pe poligon depinde de comportamentul `streamlit-folium`;
  dropdown-ul din sidebar ramane metoda stabila principala.
- Controlul de comparatie din harta foloseste tile URL-urile deja generate si nu
  reruleaza GEE, dar depinde de pluginul Leaflet side-by-side incarcat in browser.

Rezultatele reprezinta produse GEOINT preliminare de suport decizional. Extinderea
detectata automat prin Sentinel-1 SAR poate diferi de situatia reala din teren din
cauza momentului achizitiei, rezolutiei spatiale, pragurilor utilizate, zgomotului
radar, vegetatiei si limitarilor datelor auxiliare.
