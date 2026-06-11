# Sprint 11 — Performanță, stabilizare și finisare

## Obiectiv

Finalizează tool-ul nou și elimină problemele de utilizare.

## Performanță

Verifică:
- cache hit / miss;
- invalidare selectivă;
- OSM încărcat după SAR;
- schimbarea bufferului fără rerulare SAR;
- schimbarea layerelor fără rerulare;
- retry OSM;
- timeout;
- memorie;
- timp de răspuns.

## UI

Verifică:
- română consecventă;
- text clar;
- tooltip pentru parametri;
- pașii analizei;
- layere puține;
- legendă simplă;
- slider BEFORE / AFTER;
- buffer transparent;
- simboluri OSM;
- mod prezentare;
- PDF.

## Layere active implicit

```text
Județ / AOI
Apă nouă SAR
Buffer
Obiective critice
```

## Layere grupate

### Analiză SAR
- apă BEFORE;
- apă AFTER;
- apă nouă.

### Dynamic World
- BEFORE;
- AFTER;
- modificări;
- apă nouă.

### Corelare
- ambele metode;
- doar SAR;
- doar Dynamic World.

### Impact OSM
- clădiri;
- drumuri;
- căi ferate;
- poduri;
- obiective critice.

## Tooltips

Adaugă explicații pentru:
- județ;
- AOI;
- BEFORE;
- AFTER;
- polarizare;
- orbit pass;
- prag apă SAR;
- smoothing;
- connected pixels;
- buffer;
- mod prezentare;
- cache status.

## Documentație

Actualizează:
- README;
- arhitectura;
- fluxul;
- pornirea aplicației;
- cache;
- PDF;
- limitări;
- exemple.

## Test final

Execută:
- testele automate;
- checklist manual complet;
- analiză județ complet;
- analiză cu AOI;
- buffer 1;
- buffer 250;
- buffer 1000;
- PDF;
- cache;
- restart aplicație.

## La final

- rulează testele;
- pornește aplicația;
- verifică vizual;
- rulează `/diff`;
- rulează `/review`;
- afișează `git status`;
- oprește-te înainte de push.
