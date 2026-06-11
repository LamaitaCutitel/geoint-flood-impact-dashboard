# Sprint 7 — Încărcare OSM după analiza SAR

## Obiectiv

Încarcă datele OSM numai după ce apa nouă SAR a fost calculată.

## Flux

```text
analiză SAR finalizată
→ apă nouă SAR disponibilă
→ AOI activ disponibil
→ încărcare OSM
```

## Categorii

### Clădiri
```text
building=*
```

### Drumuri
```text
highway=*
```

### Căi ferate
```text
railway=*
```

### Poduri
```text
bridge=*
```

### Obiective critice
```text
amenity=hospital
amenity=clinic
amenity=pharmacy
amenity=fire_station
amenity=police
amenity=school
amenity=kindergarten
amenity=fuel
healthcare=*
emergency=*
power=*
```

## Reguli

- încarcă toate obiectele relevante din aria activă;
- nu încărca înainte de analiză;
- cache per categorie;
- progres vizibil;
- retry per categorie;
- continuă dacă o categorie eșuează;
- popup minim cu sursa OSM;
- atribuire OSM în UI și PDF.

## Jurnal

Exemplu:
```text
✓ Clădiri OSM: 18.432 obiecte
✓ Drumuri OSM: 5.841 segmente
✓ Obiective critice: 214 puncte
⚠ Infrastructură electrică: timeout
[Reîncearcă încărcarea categoriei]
```

## Teste

- încărcare după analiză;
- interdicție înainte de analiză;
- cache;
- retry;
- timeout;
- categorie lipsă;
- continuare parțială;
- atribuire.

## La final

- rulează testele;
- verifică încărcarea OSM;
- afișează `git diff --stat`;
- rulează `/review`;
- oprește-te înainte de commit.
