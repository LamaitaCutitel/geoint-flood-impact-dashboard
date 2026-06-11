# Sprint 8 — Buffer, analiză impact OSM și simboluri

## Obiectiv

Construiește bufferul în jurul apei noi și analizează elementele OSM.

## Buffer

Slider:
```text
Buffer în jurul apei noi: 1–1000 m
```

Default:
```text
250 m
```

## Afișaj

Buffer:
- portocaliu sau galben;
- umplere foarte transparentă;
- contur discret;
- vizibil pe hartă.

## Clasificare OSM

```text
Intersectat direct
În buffer de avertizare
Neexpus
```

## Clădiri
Calculează:
- număr direct;
- număr buffer;
- suprafață;
- intersecție completă / parțială.

## Drumuri
Calculează:
- km direct;
- km buffer;
- distribuție pe clase.

## Căi ferate
Calculează:
- km direct;
- km buffer;
- segmente.

## Poduri
Calculează:
- număr direct;
- număr buffer.

## Obiective critice
Pentru fiecare:
- nume;
- categorie;
- coordonate;
- distanță până la apă;
- status;
- sursă.

## Simboluri

- spital / clinică → cruce medicală;
- farmacie → cruce medicală mică;
- pompieri → flacără;
- poliție → scut;
- școală / grădiniță → simbol educație;
- benzinărie → pompă carburant;
- infrastructură electrică → fulger;
- pod → simbol pod;
- gară → tren;
- cale ferată → linie violetă;
- drum principal → linie portocalie groasă;
- clădire → poligon roșu semitransparent.

## Culoare după status

- direct: roșu intens;
- buffer: portocaliu;
- neexpus: gri discret sau ascuns implicit.

## Legendă

Include simbolurile și statusurile.

## Regula de recalculare la schimbare buffer

Recalculează numai:
- buffer;
- proximități;
- statistici OSM;
- raport.

Nu recalcula:
- SAR;
- Dynamic World;
- OSM brut.

## Teste

- buffer 1 m;
- buffer 1000 m;
- default 250;
- stil buffer;
- intersecții;
- proximități;
- simboluri;
- fallback icon;
- popup;
- recalculare selectivă.

## La final

- rulează testele;
- verifică vizual bufferul și simbolurile;
- afișează `git diff --stat`;
- rulează `/review`;
- oprește-te înainte de commit.
