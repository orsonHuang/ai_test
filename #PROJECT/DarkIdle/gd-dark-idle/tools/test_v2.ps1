param([string]$Godot = 'E:\Steam\steamapps\common\Godot Engine\godot.windows.opt.tools.64.exe')
$ErrorActionPreference = 'Stop'
$darkIdleProject = Split-Path -Parent $PSScriptRoot
$darkIdleEvidence = Join-Path (Split-Path -Parent $darkIdleProject) 'docs/verification'
$darkIdleOut = Join-Path $darkIdleEvidence 'v2-headless-tests.log'
$darkIdleErr = Join-Path $darkIdleEvidence 'v2-headless-errors.log'
$darkIdleProcess = Start-Process -FilePath $Godot -ArgumentList '--headless','--path',('"' + $darkIdleProject + '"'),'--script','res://tests/run_v2.gd' -WindowStyle Hidden -Wait -PassThru -RedirectStandardOutput $darkIdleOut -RedirectStandardError $darkIdleErr
Get-Content -LiteralPath $darkIdleErr
$darkIdleJson = Get-Content -LiteralPath $darkIdleOut -Encoding utf8 | Where-Object { $_.StartsWith('{"checks"') } | Select-Object -Last 1
if ($darkIdleProcess.ExitCode -ne 0 -or -not $darkIdleJson) { throw 'v2 tests did not return a valid result.' }
$darkIdleResult = $darkIdleJson | ConvertFrom-Json
$darkIdleJson | Set-Content -LiteralPath (Join-Path $darkIdleEvidence 'v2-rules.json') -Encoding utf8
$darkIdleResult | Select-Object passed,failed
if ($darkIdleResult.failed -gt 0) { throw 'v2 battle rules failed.' }
