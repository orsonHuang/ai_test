Start-Sleep -Seconds 90
$niteShutdownReceipt = 'D:/_Files/ai_test/#AI-NOTEBOOK/nite-monthly-20261022-shutdown/issued.json'
@{ requestedAt = (Get-Date).ToString('o'); command = 'shutdown.exe /s /t 0'; force = $false; implementationCommit = 'cf199b5af753afc7d31e819335f6d126b607b6b0'; workspaceCommit = '0277a0556c6d19d1a550aa571eb02033483cb713' } | ConvertTo-Json | Set-Content -LiteralPath $niteShutdownReceipt -Encoding UTF8
& "$env:SystemRoot/System32/shutdown.exe" /s /t 0
