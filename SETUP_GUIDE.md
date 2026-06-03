# SETUP_GUIDE

## Windows PowerShell

```powershell
git clone https://github.com/LamaitaCutitel/geoint-flood-impact-dashboard.git
cd geoint-flood-impact-dashboard
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
notepad .env
python -m src.gee.gee_auth
streamlit run app.py
```

In `.env`, completati:

```text
GEE_PROJECT_ID=your-google-cloud-project-id
```

Nu commit-uiti `.env`. Autentificarea Earth Engine se face o singura data pe fiecare
PC sau VM.

## Verificare pornire

La deschidere trebuie sa apara imediat:

- titlul aplicatiei;
- harta Romaniei cu judetele;
- dropdown-ul `Selecteaza judetul`, implicit `Galati`;
- sectiunea `Status servicii`;
- `Jurnal live de initializare si procesare`;
- formularul cu butonul `Ruleaza analiza SAR`.

Daca Google Earth Engine nu este initializat, aplicatia ramane utilizabila pentru
harta administrativa si afiseaza pasii necesari pentru autentificare.
