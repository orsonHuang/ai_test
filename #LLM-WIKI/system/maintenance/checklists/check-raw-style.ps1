[CmdletBinding()]
param([string]$Root = '')

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
if ([string]::IsNullOrWhiteSpace($Root)) { $Root = Join-Path $PSScriptRoot '../../..' }
$rootPath = (Resolve-Path -LiteralPath $Root).Path
$rawPath = Join-Path $rootPath 'raw-sources'
$files = @(Get-ChildItem -LiteralPath $rawPath -File -Filter '*.md' | Where-Object { $_.Name -notin @('README.md', 'raw-source.template.md') })
$failures = New-Object System.Collections.Generic.List[string]

foreach ($file in $files) {
    $text = [IO.File]::ReadAllText($file.FullName, [Text.Encoding]::UTF8) -replace "`r`n", "`n"
    if ($text -notmatch '(?m)^(?:[-*]\s+|\d+\.\s+|\|.+\|)') {
        $failures.Add("$($file.Name): no list or table structure")
    }
    $paragraphs = $text -split "`n`n+"
    foreach ($paragraph in $paragraphs) {
        $trimmed = $paragraph.Trim()
        if ($trimmed.Length -gt 600 -and $trimmed -notmatch '^(---|#|>|[-*]\s|\d+\.\s|\|)') {
            $failures.Add("$($file.Name): dense paragraph exceeds 600 characters")
            break
        }
    }
}

if ($failures.Count -gt 0) {
    $failures | ForEach-Object { Write-Error $_ }
    exit 1
}

Write-Output "Raw style check: PASS ($($files.Count) content files)"
