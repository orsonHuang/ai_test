$ErrorActionPreference = 'Stop'
$bundlePath = Join-Path $PSScriptRoot 'dice-monster.bundle'
$partFiles = @(Get-ChildItem -LiteralPath $PSScriptRoot -Filter 'dice-monster.bundle.part*' | Sort-Object Name)
if ($partFiles.Count -ne 6) { throw '备份分卷不完整：应有 6 个文件。' }
if (Test-Path -LiteralPath $bundlePath) { throw '目标备份已存在，请先另存现有文件。' }
$outputStream = [IO.File]::Open($bundlePath, [IO.FileMode]::CreateNew)
try {
    foreach ($partFile in $partFiles) {
        $inputStream = [IO.File]::OpenRead($partFile.FullName)
        try { $inputStream.CopyTo($outputStream) } finally { $inputStream.Dispose() }
    }
} finally { $outputStream.Dispose() }
$expectedHash = 'CF570EC1904C12C4226567E2DFAF7672F22D2991AE0B1AC81F86BC18A9B28F1B'
if ((Get-FileHash -LiteralPath $bundlePath -Algorithm SHA256).Hash -ne $expectedHash) {
    throw '备份校验失败，请重新取得完整分卷。'
}
Write-Output "备份已恢复并通过 SHA256 校验：$bundlePath"
