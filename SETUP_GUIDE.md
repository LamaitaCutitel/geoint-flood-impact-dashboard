# SETUP_GUIDE

## Windows PowerShell

Foloseste Python 3.12 sau 3.13 pentru acest proiect. Evita momentan Python 3.14,
deoarece pachete cu extensii native precum NumPy, Pandas, Folium si PyArrow pot
instala roti binare incompatibile si pot produce erori de tip
`Importing the numpy C-extensions failed`.

```powershell
git clone https://github.com/LamaitaCutitel/geoint-flood-impact-dashboard.git
cd geoint-flood-impact-dashboard
py -3.12 -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
notepad .env
python -m src.gee.gee_auth
streamlit run app.py
```

Daca `py -3.12` nu exista, instaleaza Python 3.12 de pe python.org si recreeaza
mediul virtual:

```powershell
deactivate
Remove-Item -Recurse -Force .venv
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
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
