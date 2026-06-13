# Sprint 4 — QA SAR și analiză de sensibilitate

## Obiectiv
Justifică pragul SAR final și ajută validarea vizuală.

## Modificări
- Adaugă mod QA separat, fără a schimba metodologia principală.
- Pentru polarizarea selectată rulează sweep:
  - VH: `-20`, `-19`, `-18`, `-17`, `-16`;
  - VV: `-17`, `-16`, `-15`, `-14`, `-13`.
- Pentru fiecare prag exportă:
  - apă BEFORE;
  - apă AFTER;
  - apă nouă;
  - durată;
  - status;
  - diferență procentuală față de pragul echilibrat.
- Adaugă grafic `prag dB -> apă nouă km²`.
- Adaugă layere QA opționale:
  - apă persistentă;
  - pierdere de apă;
  - delta backscatter AFTER - BEFORE.
- Păstrează layerele QA ascunse implicit.
- Adaugă tabel pentru justificarea pragului în raport.
- Adaugă checklist manual pentru:
  - luciu de apă existent;
  - umbre radar;
  - teren urban;
  - vegetație inundată;
  - artefacte la marginea scenei.

## Teste
- sweep produce valori și statusuri;
- graficul lipsește dacă valorile lipsesc;
- layerele QA ascunse implicit;
- pragul final exportat.
