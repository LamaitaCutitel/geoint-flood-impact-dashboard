# Sprint 4 — Dynamic World și PDF

## Obiectiv
Reduce latența, îmbunătățește diagnosticul și curăță raportul.

## Dynamic World
- Dacă acoperirea observației individuale `< 0.85`, folosește mozaic fallback.
- Afișează:
  - perioadă căutată;
  - dată efectivă;
  - acoperire;
  - tip produs;
  - erori tile.
- Status general `reușit` doar dacă există tile-uri obligatorii:
  - BEFORE;
  - AFTER;
  - apă nouă Dynamic World.
- Grupează metricile într-o imagine multi-band și un singur `reduceRegion`.
- Pentru OSM × Dynamic World:
  - clădiri = clasă dominantă pe suprafață;
  - drumuri/căi ferate = eșantionare pe segmentul afectat;
  - poduri și puncte = punct reprezentativ.

## PDF
- Invalidează cache-ul PDF la orice schimbare analitică.
- Elimină dicționarele brute din text.
- Transformă rezultatele în:
  - tabele;
  - paragrafe lizibile;
  - grafice separate;
  - valori rotunjite.
- Adaugă scară reală în hartă.
- Include:
  - SAR;
  - Dynamic World;
  - OSM;
  - completitudine;
  - surse;
  - data cache;
  - limitări;
  - timpi.

## Teste
- coverage sub 85% → mozaic;
- status verde doar cu tile-uri obligatorii;
- un singur reduceRegion pentru metrici;
- PDF regenerat după recalculare;
- fără JSON brut;
- scară reală.
