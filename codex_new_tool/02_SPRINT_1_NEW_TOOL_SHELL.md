# Sprint 1 — Creează tool-ul nou și interfața de bază

## Obiectiv

Creează un tool nou, separat logic de dashboard-ul experimental, cu o interfață simplă și clară.

## Denumire

```text
Evaluarea impactului unei inundații
```

Subtitlu:

```text
Analiză multisursă SAR, Dynamic World și OpenStreetMap
```

## Referință UI

Folosește imaginea:

```text
reference_ui/evaluare_impact_inundatie_mockup.png
```

ca reper vizual.

## Structură

### Antet
- titlu;
- subtitlu;
- status `GEE conectat`;
- `Județ`;
- `AOI activ / inactiv`;
- buton principal:
  - `Generează și descarcă raportul PDF`.

### Coloană stângă
- pașii analizei;
- județ;
- AOI;
- imagine BEFORE;
- imagine AFTER;
- slider buffer;
- buton `Rulează analiza impactului`;
- preview swipe.

### Hartă centrală
- basemap color;
- România la pornire;
- județe prin contur;
- zoom pe județ;
- AOI, dacă există;
- layer-ele rezultat.

### Coloană dreaptă
- layere grupate;
- legendă contextuală simplă.

### Tab-uri
- `Hartă`;
- `Rezumat impact`;
- `Dynamic World`;
- `Elemente OSM`;
- `Raport`.

## Wizard

Afișează:

```text
1. Selectează județul
2. Desenează AOI (opțional)
3. Alege imaginile BEFORE și AFTER
4. Compară imaginile
5. Rulează analiza impactului
6. Generează raportul PDF
```

## Reguli

- UI integral în română;
- harta domină layout-ul;
- nu afișa layere tehnice;
- nu implementa încă procesarea;
- nu încărca OSM;
- nu implementa încă PDF-ul.

## Teste

Adaugă teste pentru:
- randarea paginii;
- existența tab-urilor;
- wizard;
- statusuri;
- buton raport dezactivat înainte de analiză.

## La final

- rulează testele;
- pornește aplicația;
- verifică layout-ul;
- afișează `git diff --stat`;
- rulează `/review`;
- oprește-te înainte de commit.
