[CmdletBinding()]
param([string]$Root = '')

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
if ([string]::IsNullOrWhiteSpace($Root)) { $Root = Join-Path $PSScriptRoot '../../..' }
$rootPath = (Resolve-Path -LiteralPath $Root).Path
$failures = New-Object System.Collections.Generic.List[string]

function Convert-UnicodeLiteral {
    param([string]$Escaped)
    return ConvertFrom-Json ('"' + $Escaped + '"')
}

$requirements = [ordered]@{
    'system/protocols/RUNTIME_ROUTING.md' = @('README.md', 'COMMAND_MANUAL.md', 'system/protocols/QUERY_PROTOCOL.md', 'system/protocols/INGEST_PROTOCOL.md')
    'system/protocols/QUERY_PROTOCOL.md' = @('L0', 'L1', 'L2', 'Web', 'quick-reference.md', 'KNOWLEDGE_SCOPE.md')
    'system/protocols/INGEST_PROTOCOL.md' = @('SCORING_SYSTEM.md', 'MODEL_ROUTING.md', 'ingest-stage-gates.md')
    'agents/BUILD_GUIDE.md' = @('agent_type', 'role', 'context', 'personal', 'none', 'L0')
    'agents/EXPERT_PROTOCOL.md' = @('ContextBrief', 'QUERY_PROTOCOL.md', 'BUILD_GUIDE.md')
    'agents/CONTEXT_CONTRACT.md' = @('task:', 'constraints:', 'locked_decisions:', 'available_evidence:')
    'COMMAND_MANUAL.md' = @('QUERY_PROTOCOL.md', 'INGEST_PROTOCOL.md', 'EXPERT_PROTOCOL.md')
    'README.md' = @(
        (Convert-UnicodeLiteral '\u521d\u59cb\u5316'),
        (Convert-UnicodeLiteral '\u76f4\u63a5\u63d0\u95ee\u4e0e\u67e5\u8be2'),
        (Convert-UnicodeLiteral '\u5185\u5bb9\u5165\u5e93'),
        (Convert-UnicodeLiteral '\u4e13\u5bb6\u6a21\u5f0f'),
        (Convert-UnicodeLiteral '\u5065\u5eb7\u68c0\u67e5')
    )
}

$readmeText = [IO.File]::ReadAllText((Join-Path $rootPath 'README.md'), [Text.Encoding]::UTF8)
$runtimeRoutingText = [IO.File]::ReadAllText((Join-Path $rootPath 'system/protocols/RUNTIME_ROUTING.md'), [Text.Encoding]::UTF8)
if (-not $readmeText.Contains('system/protocols/RUNTIME_ROUTING.md')) { $failures.Add('README.md does not point to RUNTIME_ROUTING.md') }
if ($readmeText.Contains((Convert-UnicodeLiteral '## \u6587\u4ef6\u8def\u7531'))) { $failures.Add('README.md still owns the detailed file-routing section') }
if (-not $runtimeRoutingText.Contains((Convert-UnicodeLiteral '\u540c\u4e00\u4efb\u52a1\u7684\u540e\u7eed\u6d88\u606f'))) { $failures.Add('RUNTIME_ROUTING.md does not define follow-up behavior') }
if (-not $runtimeRoutingText.Contains((Convert-UnicodeLiteral '\u4e0d\u5f97\u5728\u6bcf\u6761\u6d88\u606f\u4e2d\u5b8c\u6574\u626b\u63cf'))) { $failures.Add('RUNTIME_ROUTING.md still permits per-message COMMAND_MANUAL scanning') }

foreach ($entry in $requirements.GetEnumerator()) {
    $path = Join-Path $rootPath $entry.Key
    if (-not (Test-Path -LiteralPath $path)) {
        $failures.Add("Missing file: $($entry.Key)")
        continue
    }
    $text = [IO.File]::ReadAllText($path, [Text.Encoding]::UTF8)
    foreach ($token in $entry.Value) {
        if (-not $text.Contains($token)) { $failures.Add("$($entry.Key): missing token $token") }
    }
}

$nowText = [IO.File]::ReadAllText((Join-Path $rootPath 'NOW.md'), [Text.Encoding]::UTF8)
$statusText = [IO.File]::ReadAllText((Join-Path $rootPath 'system/registry/KNOWLEDGE_STATUS.md'), [Text.Encoding]::UTF8)
$fullWidthColon = Convert-UnicodeLiteral '\uff1a'
$snapshotLabels = @('domain', 'Wiki', 'raw', (Convert-UnicodeLiteral '\u96f6\u5f15\u7528 raw'))
foreach ($label in $snapshotLabels) {
    $statusMatch = [regex]::Match($statusText, '(?m)^\|\s*' + [regex]::Escape($label) + '\s*\|\s*(?<count>\d+)\s*\|')
    $nowMatch = [regex]::Match($nowText, '(?m)^-\s*' + [regex]::Escape($label + $fullWidthColon) + '(?<count>\d+)')
    if (-not $statusMatch.Success) { $failures.Add("KNOWLEDGE_STATUS.md missing snapshot: $label") }
    if (-not $nowMatch.Success) { $failures.Add("NOW.md missing snapshot: $label") }
    if ($statusMatch.Success -and $nowMatch.Success -and $statusMatch.Groups['count'].Value -ne $nowMatch.Groups['count'].Value) {
        $failures.Add("NOW.md snapshot drift: $label")
    }
}

$requiredNowHeadings = @(
    (Convert-UnicodeLiteral '## \u5feb\u901f\u5feb\u7167'),
    (Convert-UnicodeLiteral '## \u5f53\u524d\u9636\u6bb5'),
    (Convert-UnicodeLiteral '## \u5f53\u524d\u7126\u70b9'),
    (Convert-UnicodeLiteral '## \u4e0b\u4e00\u6b65'),
    (Convert-UnicodeLiteral '## \u672a\u7ed3\u5c3e\u5df4'),
    (Convert-UnicodeLiteral '## \u7ef4\u62a4\u89c4\u5219')
)
foreach ($heading in $requiredNowHeadings) {
    if (-not $nowText.Contains($heading)) { $failures.Add("NOW.md missing fixed section: $heading") }
}
if ($nowText.Contains((Convert-UnicodeLiteral '## \u6700\u8fd1\u8fdb\u5c55'))) { $failures.Add('NOW.md must not contain a recent-progress section') }
if (($nowText -split "`n").Count -gt 45) { $failures.Add('NOW.md exceeds the 45-line maintenance limit') }
if (-not $nowText.Contains((Convert-UnicodeLiteral '\u80fd\u529b\uff1a\u7a7a\u5e93'))) { $failures.Add('NOW.md missing empty capability summary') }
if (-not $statusText.Contains((Convert-UnicodeLiteral '\u5c1a\u65e0\u77e5\u8bc6\u5185\u5bb9'))) { $failures.Add('KNOWLEDGE_STATUS.md missing empty capability status') }

$healthDateLabel = Convert-UnicodeLiteral '\u6700\u8fd1\u5b8c\u6574\u5065\u5eb7\u68c0\u67e5\uff1a'
$statusHealthDate = [regex]::Match($statusText, '(?m)^>\s*' + [regex]::Escape($healthDateLabel) + '(?<value>[^\r\n]+)')
$nowHealthDate = [regex]::Match($nowText, '(?m)^-\s*' + [regex]::Escape($healthDateLabel) + '(?<value>[^\r\n]+)')
if (-not ($statusHealthDate.Success -and $nowHealthDate.Success -and $statusHealthDate.Groups['value'].Value.Trim() -eq $nowHealthDate.Groups['value'].Value.Trim())) {
    $failures.Add('NOW.md health-check date does not match KNOWLEDGE_STATUS.md')
}

$statusNextAnchor = [regex]::Match($statusText, (Convert-UnicodeLiteral '\u4e0b\u4e00\u951a\u70b9\uff1a') + '(?<value>\d+)')
$nowNextAnchor = [regex]::Match($nowText, (Convert-UnicodeLiteral '\u4e0b\u4e00\u56de\u6d4b\u951a\u70b9\uff1a') + '(?<value>\d+)')
if (-not ($statusNextAnchor.Success -and $nowNextAnchor.Success -and $statusNextAnchor.Groups['value'].Value -eq $nowNextAnchor.Groups['value'].Value)) {
    $failures.Add('NOW.md next regression anchor does not match KNOWLEDGE_STATUS.md')
}

if ($failures.Count -gt 0) {
    $failures | ForEach-Object { Write-Error $_ }
    exit 1
}

Write-Output 'Query/Agent contract: PASS'
