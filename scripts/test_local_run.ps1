param(
    [int]$Port = 8510,
    [switch]$SkipFullTests
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path $PSScriptRoot -Parent
Set-Location $projectRoot
$started = Get-Date
$logDirectory = Join-Path $projectRoot ".codex-sprint-logs"
New-Item -ItemType Directory -Force -Path $logDirectory | Out-Null

$venvPath = if (Test-Path ".venv312\Scripts\python.exe") {
    ".venv312"
} else {
    ".venv"
}
$python = Join-Path $venvPath "Scripts\python.exe"
if (-not (Test-Path $python)) {
    throw "Mediul Python lipseste. Ruleaza mai intai .\scripts\start_app.ps1."
}

$checks = [System.Collections.Generic.List[string]]::new()
& $python -c "import streamlit, folium, ee, shapely, pyproj, reportlab, matplotlib; import impact_tool"
if ($LASTEXITCODE -ne 0) { throw "Importurile Python au esuat." }
$checks.Add("- Importuri Python: PASS")

@(
    "impact_tool.py",
    "data\boundaries\romania_counties.geojson",
    "scripts\prepare_galati_cache.py",
    "requirements.txt",
    "requirements-impact-tool.txt"
) | ForEach-Object {
    if (-not (Test-Path $_)) {
        throw "Fisier obligatoriu lipsa: $_"
    }
}
$checks.Add("- Fisiere obligatorii: PASS")

& $python scripts\prepare_galati_cache.py 2>&1 |
    Tee-Object -FilePath (Join-Path $logDirectory "prepare-galati-cache.log")
if ($LASTEXITCODE -ne 0) { throw "Pregatirea cache-ului OSM Galati a esuat." }
$checks.Add("- Cache OSM Galati: PASS")

if (-not $SkipFullTests) {
    & $python -m pytest -q --basetemp=.pytest-tmp-local-run 2>&1 |
        Tee-Object -FilePath (Join-Path $logDirectory "pytest-local-run.log")
    if ($LASTEXITCODE -ne 0) { throw "Testele pytest au esuat." }
    $checks.Add("- Pytest complet: PASS")
}

$streamlitLog = Join-Path $logDirectory "streamlit-local-run.log"
$job = Start-Job -ScriptBlock {
    param($PythonPath, $ProjectRoot, $ServerPort)
    Set-Location $ProjectRoot
    & $PythonPath -m streamlit run impact_tool.py `
        --server.headless true `
        --server.address 127.0.0.1 `
        --server.port $ServerPort 2>&1
} -ArgumentList $python, $projectRoot, $Port

try {
    $healthy = $false
    for ($attempt = 0; $attempt -lt 30; $attempt++) {
        Start-Sleep -Seconds 1
        try {
            $response = Invoke-WebRequest "http://127.0.0.1:$Port/_stcore/health" -UseBasicParsing
            if ($response.StatusCode -eq 200 -and $response.Content -match "ok") {
                $healthy = $true
                break
            }
        } catch {
            # Streamlit may still be starting.
        }
    }
    if (-not $healthy) {
        throw "Health check-ul Streamlit nu a raspuns in 30 secunde."
    }
    $checks.Add("- Streamlit health check: PASS")
} finally {
    if ($job.State -eq "Running") {
        Stop-Job $job
    }
    Receive-Job $job -Wait | Set-Content -Path $streamlitLog -Encoding UTF8
    Remove-Job $job -Force
}

$finished = Get-Date
$report = @(
    "# Local Run Report",
    "",
    "Data: $($finished.ToString('yyyy-MM-dd HH:mm:ss zzz'))",
    "Python: $(& $python --version)",
    "Port smoke test: $Port",
    "Durata: $([math]::Round(($finished - $started).TotalSeconds, 2)) secunde",
    "",
    "## Verificari",
    ""
) + $checks + @(
    "",
    "## Observatii",
    "",
    "- Testul automat nu executa o analiza GEE completa si nu confirma situatia din teren.",
    "- Fluxul vizual, selectia scenelor si descarcarea PDF necesita verificare in browser.",
    "- Logurile brute sunt in `.codex-sprint-logs/` si nu sunt versionate."
)
$report | Set-Content -Path "LOCAL_RUN_REPORT.md" -Encoding UTF8
Write-Host "Toate verificarile locale au trecut."
