# Sprint 6 — Dynamic World BEFORE / AFTER și corelare multisursă

## Obiectiv

Adaugă analiza Dynamic World relevantă pentru tool.

## Layer-e

```text
Dynamic World BEFORE
Dynamic World AFTER
Modificări observate Dynamic World
Apă nouă evidențiată prin Dynamic World
```

## Logică apă nouă

```text
Dynamic World AFTER = water
AND
Dynamic World BEFORE != water
```

## Tranziții către apă

Calculează:
- crops → water;
- grass → water;
- built → water;
- trees → water;
- flooded vegetation → water;
- shrub and scrub → water;
- bare → water.

Afișează implicit numai tranzițiile relevante.

## Corelare SAR × Dynamic World

Calculează:
```text
Apă nouă prin ambele metode
Apă nouă doar SAR
Apă nouă doar Dynamic World
```

## Simbolizare

- ambele metode: verde intens;
- doar SAR: cyan;
- doar Dynamic World: mov.

## Statistici

- suprafață apă nouă Dynamic World;
- suprafață comună;
- suprafață doar SAR;
- suprafață doar Dynamic World;
- tranziții către apă.

## Grafice

Generează date pentru:
- suprafețe apă;
- tranziții Dynamic World.

## Teste

- BEFORE;
- AFTER;
- new water;
- transitions;
- overlap;
- only SAR;
- only Dynamic World;
- grafice.

## La final

- rulează testele;
- verifică layerele;
- afișează `git diff --stat`;
- rulează `/review`;
- oprește-te înainte de commit.
