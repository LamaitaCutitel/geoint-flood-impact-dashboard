param(
    [string]$OutputDirectory = "export_review",
    [switch]$IncludeOsmCache
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$packageName = "geoint-flood-impact-dashboard-review-$timestamp"
$stagingRoot = Join-Path $OutputDirectory $packageName
$zipPath = Join-Path $OutputDirectory "$packageName.zip"
New-Item -ItemType Directory -Force -Path $stagingRoot | Out-Null
$projectRoot = (Resolve-Path $PSScriptRoot).Path.TrimEnd("\")

function Get-ReviewRelativePath {
    param(
        [string]$Root,
        [string]$FullName
    )
    return $FullName.Substring($Root.Length).TrimStart("\")
}

$excludedDirectories = @(
    ".git", ".venv", ".venv312", "venv", "env", "__pycache__",
    ".pytest_cache", ".codex-sprint-logs", "export_review",
    "data\output", "data\cache", "Codex_Overnight_Disertatie_GEOINT"
)
if (-not $IncludeOsmCache) {
    $excludedDirectories += "cache"
}
$excludedExtensions = @(".tif", ".tiff", ".zip", ".pyc")

$files = Get-ChildItem -File -Recurse -ErrorAction SilentlyContinue | Where-Object {
    $relative = Get-ReviewRelativePath -Root $projectRoot -FullName $_.FullName
    $directoryExcluded = $excludedDirectories | Where-Object {
        $relative -eq $_ -or $relative.StartsWith("$($_)\")
    }
    $isSecret = (
        $_.Name -eq ".env" -or
        ($_.Name -like ".env.*" -and $_.Name -ne ".env.example") -or
        $_.Name -eq "secrets.toml" -or
        $_.Name -like "*service-account*.json" -or
        $_.Name -like "*service_account*.json" -or
        $_.Name -like "credentials*.json" -or
        $_.Name -like "token*.json"
    )
    $isTestTemporary = $relative -like ".pytest-*"
    -not $directoryExcluded -and -not $isSecret -and -not $isTestTemporary -and
        $excludedExtensions -notcontains $_.Extension.ToLowerInvariant()
}

foreach ($file in $files) {
    $relative = Get-ReviewRelativePath -Root $projectRoot -FullName $file.FullName
    $destination = Join-Path $stagingRoot $relative
    New-Item -ItemType Directory -Force -Path (Split-Path $destination) | Out-Null
    Copy-Item -LiteralPath $file.FullName -Destination $destination
}

$manifestRows = Get-ChildItem $stagingRoot -File -Recurse | ForEach-Object {
    $relative = Get-ReviewRelativePath -Root (Resolve-Path $stagingRoot).Path -FullName $_.FullName
    $hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $_.FullName).Hash
    "$relative`t$($_.Length)`t$hash"
}
@("path`tbytes`tsha256") + $manifestRows |
    Set-Content -Path (Join-Path $stagingRoot "EXPORT_MANIFEST.tsv") -Encoding UTF8

Compress-Archive -Path "$stagingRoot\*" -DestinationPath $zipPath -CompressionLevel Optimal

$maxPartBytes = 500MB
$zip = Get-Item $zipPath
if ($zip.Length -gt $maxPartBytes) {
    $input = [IO.File]::OpenRead($zipPath)
    try {
        $buffer = New-Object byte[] $maxPartBytes
        $part = 1
        while (($read = $input.Read($buffer, 0, $buffer.Length)) -gt 0) {
            $partPath = "{0}.part{1:D3}" -f $zipPath, $part
            $output = [IO.File]::Create($partPath)
            try {
                $output.Write($buffer, 0, $read)
            } finally {
                $output.Dispose()
            }
            $part++
        }
    } finally {
        $input.Dispose()
    }
}

Write-Host "Pachet creat: $zipPath"
Write-Host "Cache OSM inclus: $IncludeOsmCache"
