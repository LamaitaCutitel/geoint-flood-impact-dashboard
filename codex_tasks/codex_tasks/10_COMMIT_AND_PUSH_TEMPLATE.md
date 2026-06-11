# Template commit și push

După fiecare sprint:

```powershell
git status
git diff --stat
pytest
git add .
git commit -m "<mesaj sprint>"
git push
```

Mesaje recomandate:

```text
Reset county dependent Streamlit state
Improve SAR recommendations and GEE error handling
Separate BEFORE baseline and AFTER peak SAR strategies
Stabilize layer comparison and centralize map styles
Optimize Dynamic World timing and lazy load optional layers
Add OSM operational impact assessment
Add Copernicus EMS validation metrics
```
