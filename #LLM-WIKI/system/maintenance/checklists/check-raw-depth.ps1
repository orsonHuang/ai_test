[CmdletBinding()]
param([string]$Root = '')

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
if ([string]::IsNullOrWhiteSpace($Root)) { $Root = Join-Path $PSScriptRoot '../../..' }
$rootPath = (Resolve-Path -LiteralPath $Root).Path
$rawPath = Join-Path $rootPath 'raw-sources'
$files = @(Get-ChildItem -LiteralPath $rawPath -File -Filter '*.md' | Where-Object { $_.Name -notin @('README.md', 'raw-source.template.md') })
$failures = New-Object System.Collections.Generic.List[string]
$requiredFields = @('title', 'source', 'source_url', 'source_date', 'ingested_at', 'language', 'topics', 'ingest_verdict', 'ingest_score')

foreach ($file in $files) {
    $text = [IO.File]::ReadAllText($file.FullName, [Text.Encoding]::UTF8)
    if (-not $text.StartsWith("---`n") -and -not $text.StartsWith("---`r`n")) {
        $failures.Add("$($file.Name): missing YAML frontmatter")
    }
    foreach ($field in $requiredFields) {
        if ($text -notmatch ('(?m)^' + [regex]::Escape($field) + ':')) {
            $failures.Add("$($file.Name): missing field $field")
        }
    }
    $sections = [regex]::Matches($text, '(?m)^##\s+').Count
    if ($sections -lt 2) { $failures.Add("$($file.Name): fewer than two content sections") }
}

if ($failures.Count -gt 0) {
    $failures | ForEach-Object { Write-Error $_ }
    exit 1
}

Write-Output "Raw depth check: PASS ($($files.Count) content files)"
