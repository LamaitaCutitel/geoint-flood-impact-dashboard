# Probleme rămase înainte de predarea disertației

## Critice

### 1. Fluxul Galați nu a fost executat cap-coadă în browser

- **Descriere:** nu există o rulare manuală completă cu selecția scenelor Sentinel-1 finale, comparație, analiză rapidă, analiză detaliată, Dynamic World, impact OSM și raport PDF final.
- **Impact:** valorile studiului de caz nu pot fi incluse încă în forma finală a disertației.
- **Prioritate:** critică.
- **Recomandare:** rulează fluxul complet în browser și completează fișierele `results_summary.json`, `results_summary.csv` și secțiunile marcate din handoff.
- **Trebuie rezolvat înainte de predare:** da.

### 2. Scenele Sentinel-1 finale nu sunt validate

- **Descriere:** perechea BEFORE/AFTER nu este consemnată în pachet.
- **Impact:** metodologia nu poate fi documentată complet, iar rezultatele nu pot fi reproduse.
- **Prioritate:** critică.
- **Recomandare:** selectează scene compatibile, notează ID-urile, datele, orbita, polarizarea și acoperirea.
- **Trebuie rezolvat înainte de predare:** da.

### 3. Raportul PDF final cu date reale nu este disponibil în repository

- **Descriere:** generatorul PDF este testat structural, însă raportul final nu este versionat și nu a fost validat vizual.
- **Impact:** raportul nu poate fi anexat încă la lucrare.
- **Prioritate:** critică.
- **Recomandare:** generează raportul după rularea finală, verifică vizual coperta, harta, graficele și tabelele, apoi copiază-l în pachet.
- **Trebuie rezolvat înainte de predare:** da, dacă raportul este folosit ca anexă.

### 4. Capturile pentru disertație nu sunt generate

- **Descriere:** capturile reale lipsesc; în repository există doar instrucțiuni și fișiere placeholder.
- **Impact:** capitolul studiului de caz nu poate fi ilustrat complet.
- **Prioritate:** critică.
- **Recomandare:** urmează pașii din `docs/screenshots/dissertation_final/` și salvează imaginile la minimum `1440 × 900`.
- **Trebuie rezolvat înainte de predare:** da.

## Importante

### 5. Verificarea vizuală Dynamic World lipsește

- **Descriere:** codul și testele structurale există, dar layerele reale nu au fost inspectate manual.
- **Impact:** interpretarea multisursă poate fi incompletă.
- **Prioritate:** importantă.
- **Recomandare:** verifică datele efective BEFORE/AFTER, acoperirea, tipul produsului și corelarea cu SAR.
- **Trebuie rezolvat înainte de predare:** da, dacă Dynamic World este prezentat în rezultate.

### 6. Pragul SAR final nu este justificat prin testare vizuală

- **Descriere:** pragul rămâne ajustabil, dar valoarea finală utilizată în studiul de caz nu este consemnată.
- **Impact:** rezultatul nu poate fi reprodus și discutat metodologic complet.
- **Prioritate:** importantă.
- **Recomandare:** testează valori apropiate și documentează alegerea finală.
- **Trebuie rezolvat înainte de predare:** da.

### 7. Interpretarea elementelor OSM necesită control manual

- **Descriere:** intersecția geometrică și bufferul indică expunere potențială, nu pagubă reală.
- **Impact:** există risc de supra-interpretare.
- **Prioritate:** importantă.
- **Recomandare:** inspectează lista elementelor prioritare și folosește formulări prudente.
- **Trebuie rezolvat înainte de predare:** da.

## Opționale

### 8. Validare cu observații din teren

- **Descriere:** rezultatele automate nu au fost comparate cu surse independente.
- **Impact:** limitarea nu blochează descrierea prototipului, dar reduce robustețea concluziilor.
- **Prioritate:** opțională, recomandată.
- **Recomandare:** compară cu rapoarte oficiale, produse Copernicus EMS sau observații disponibile.
- **Trebuie rezolvat înainte de predare:** nu, dar trebuie menționată ca limitare.

### 9. Extinderea pachetului offline

- **Descriere:** cache-ul OSM local este exclus implicit din exportul curat.
- **Impact:** o demonstrație fără internet necesită pregătire suplimentară.
- **Prioritate:** opțională.
- **Recomandare:** folosește exportul cu opțiunea `-IncludeOsmCache` pentru un pachet local mai mare.
- **Trebuie rezolvat înainte de predare:** nu.
