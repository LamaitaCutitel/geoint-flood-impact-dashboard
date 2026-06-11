# Sprint 9 — Funcții suplimentare pentru hartă

## Obiectiv

Adaugă funcții utile, fără să aglomerezi interfața.

## Identify

Buton:
```text
Identifică informații
```

Prin click pe hartă afișează:
- coordonate;
- valoare SAR BEFORE / AFTER;
- pixel apă Da / Nu;
- clasă Dynamic World BEFORE / AFTER;
- detalii OSM dacă există obiect;
- distanță până la apa nouă;
- status OSM.

## Measure

Adaugă:
- măsoară distanța;
- măsoară suprafața.

## Navigare

Adaugă:
- revino la România;
- centrează pe județ;
- zoom pe layer activ;
- fullscreen.

## Reset

Adaugă:
- șterge AOI;
- curăță selecția BEFORE / AFTER;
- curăță rezultatele;
- reia analiza.

## Filtre OSM

Checkbox:
- clădiri;
- drumuri;
- căi ferate;
- poduri;
- obiective critice.

Subcategorii:
- unități medicale;
- pompieri;
- poliție;
- școli;
- farmacii;
- benzinării;
- infrastructură electrică.

## Mod prezentare

Buton:
```text
Afișează doar impactul critic
```

Păstrează:
- apă nouă SAR;
- buffer;
- drumuri importante;
- poduri;
- obiective critice.

Ascunde:
- clădiri obișnuite;
- elemente neexpuse;
- detalii secundare.

## Export avansat discret

Opțional:
- CSV;
- GeoJSON.

Nu afișa aceste exporturi ca acțiuni principale.

## Teste

- Identify;
- Measure;
- navigare;
- reset;
- filtre;
- mod prezentare;
- export avansat.

## La final

- rulează testele;
- verifică manual;
- afișează `git diff --stat`;
- rulează `/review`;
- oprește-te înainte de commit.
