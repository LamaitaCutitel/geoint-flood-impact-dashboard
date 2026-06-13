# Audit tehnic SAR — rezumat pentru Codex

## Puncte validate static
- metoda principală folosește scene individuale BEFORE/AFTER;
- colecția este filtrată la AOI, interval, IW, polarizare și opțional orbit pass;
- masca de apă folosește prag dB și filtrare prin pixeli conectați;
- apa nouă este `AFTER AND NOT BEFORE`;
- aplicația calculează apă persistentă și pierdere de apă;
- OSM se procesează după vectorizarea apei noi;
- PDF-ul și UI-ul afișează indicatorii SAR.

## Probleme prioritare
1. schimbarea parametrilor SAR nu invalidează automat rezultatul anterior;
2. erorile metricilor pot deveni `0.0`;
3. erorile vectorizării pot deveni `None`;
4. vectorizarea folosește fix `30 m`, metricile implicit `10 m`;
5. `bestEffort=True` poate modifica efectiv scara fără diagnostic;
6. orbita relativă diferită este doar avertisment;
7. pragurile VH/VV existente nu sunt integrate în UI;
8. tile errors pot fi mascate;
9. lipsesc analiza de sensibilitate și justificarea pragului;
10. rezultatele reale Galați nu sunt încă validate cap-coadă.
