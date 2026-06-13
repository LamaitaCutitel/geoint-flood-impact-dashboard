# Checklist capturi pentru disertație

Capturile reale nu sunt încă generate. Acest folder este pregătit pentru validarea manuală a fluxului Galați.

## Condiții înainte de captură

1. Rulează:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\test_local_run.ps1
.\scripts\start_app.ps1
```

2. Verifică:

- status GEE conectat;
- presetul `Inundații Galați — septembrie 2024`;
- cache Galați valid;
- lipsa terminalului și a credentialelor în cadru;
- rezoluție minimă recomandată: `1440 × 900`.

## Ordinea capturilor

### `01-startup.png`

Conținut:
- titlul aplicației;
- statusul GEE;
- județul Galați;
- harta României;
- sidebar-ul cu pașii fluxului.

Legendă propusă pentru lucrare:

> Interfața inițială a aplicației pentru configurarea analizei GEOINT preliminare.

### `02-scene-selection.png`

Conținut:
- exploratorul temporal Sentinel-1;
- thumbnail-uri vizibile;
- perechea BEFORE/AFTER selectată;
- metadatele scenelor.

Legendă propusă:

> Selectarea manuală a scenelor Sentinel-1 BEFORE și AFTER utilizate în analiza SAR.

### `03-before-after-swipe.png`

Conținut:
- comparatorul vertical activ;
- etichetele BEFORE și AFTER;
- separatorul poziționat central.

Legendă propusă:

> Compararea vizuală a scenelor Sentinel-1 prin separatorul vertical BEFORE/AFTER.

### `04-sar-results.png`

Conținut:
- layer-ul apă nouă SAR;
- bufferul activ;
- legenda;
- aria analizată.

Legendă propusă:

> Extinderea preliminară a apei observate automat prin analiza SAR și bufferul de avertizare.

### `05-dynamic-world.png`

Conținut:
- tab-ul Dynamic World;
- datele efective BEFORE/AFTER;
- acoperirea;
- tipul produsului;
- diferențele observate.

Legendă propusă:

> Analiza diferențelor observate Dynamic World și corelarea multisursă cu rezultatul SAR.

### `06-osm-impact.png`

Conținut:
- clădiri, drumuri, poduri și obiective critice;
- simboluri;
- sursa cache/live;
- completitudinea;
- tabelul de priorități.

Legendă propusă:

> Elemente OpenStreetMap potențial expuse, identificate prin intersecție geometrică și proximitate față de apa nouă.

### `07-pdf-report.png`

Conținut:
- coperta raportului PDF;
- harta sintetică;
- nota privind caracterul preliminar al produsului.

Legendă propusă:

> Raportul PDF generat automat pentru documentarea rezultatelor analizei GEOINT preliminare.

## Reguli

- Nu include `.env`, credentiale, token-uri sau date personale.
- Nu prezenta capturile ca dovadă de confirmare oficială din teren.
- Folosește în lucrare formulările `extindere preliminară`, `element potențial expus` și `necesită verificare în teren`.
