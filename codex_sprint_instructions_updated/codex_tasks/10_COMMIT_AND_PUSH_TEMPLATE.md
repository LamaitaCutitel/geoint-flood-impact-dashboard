# Template după fiecare sprint

După testare și review:

```powershell
git status
git diff --stat
pytest
git add .
git commit -m "<mesaj clar pentru sprint>"
git push
```

Mesaje recomandate:

```text
Sprint 1: Reset county dependent Streamlit state
Sprint 2: Improve SAR recommendations and GEE error handling
Sprint 3: Separate BEFORE baseline and AFTER peak SAR strategies
Sprint 4: Stabilize layer comparison and centralize map styles
Sprint 5: Optimize Dynamic World timing and lazy load optional layers
Sprint 6: Add OSM operational impact assessment
Sprint 7: Add Copernicus EMS validation metrics
Sprint 8: Improve grouped layers legend and professional HTML report
```
