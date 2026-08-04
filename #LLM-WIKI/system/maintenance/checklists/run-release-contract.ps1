[CmdletBinding()]
param([string]$Root)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
if ([string]::IsNullOrWhiteSpace($Root)) { $Root = Join-Path $PSScriptRoot '../../..' }
$rootPath = (Resolve-Path -LiteralPath $Root).Path
$failures = New-Object System.Collections.Generic.List[string]

$requiredFiles = @(
    'README.md', 'AGENTS.md', 'COMMAND_MANUAL.md', 'NOW.md', '.gitignore',
    'Clippings/README.md',
    'raw-sources/README.md', 'raw-sources/raw-source.template.md',
    'wiki/README.md', 'wiki/wiki.template.md',
    'domains/README.md', 'domains/domain.template.md',
    'agents/README.md', 'agents/BUILD_GUIDE.md', 'agents/EXPERT_PROTOCOL.md',
    'agents/CONTEXT_CONTRACT.md', 'agents/prompts/README.md',
    'agents/prompts/expert-role.template.md', 'agents/prompts/expert-context.template.md',
    'system/README.md',
    'system/protocols/RUNTIME_ROUTING.md',
    'system/protocols/QUERY_PROTOCOL.md', 'system/protocols/INGEST_PROTOCOL.md',
    'system/protocols/SCORING_SYSTEM.md', 'system/protocols/MODEL_ROUTING.md',
    'system/protocols/WIKI-LINK-STANDARD.md',
    'system/registry/KNOWLEDGE_SCOPE.md', 'system/registry/KNOWLEDGE_STATUS.md',
    'system/registry/index.md', 'system/registry/quick-reference.md',
    'system/registry/raw-list.md', 'system/registry/skipped-sources.md',
    'system/integrations/README.md', 'system/integrations/IMA-GUIDE.md',
    'system/integrations/ima-config.template.json',
    'system/maintenance/README.md', 'system/maintenance/SETUP.md',
    'system/maintenance/CHANGELOG.md',
    'system/maintenance/CHANGELOG_archive/README.md',
    'system/maintenance/initialize-knowledge.ps1',
    'system/maintenance/setup-wizard.ps1', 'system/maintenance/setup-wizard.zh-CN.json',
    'system/maintenance/checklists/README.md',
    'system/maintenance/checklists/initialization-check.md',
    'system/maintenance/checklists/ingest-stage-gates.md',
    'system/maintenance/checklists/knowledge-health-check.md',
    'system/maintenance/checklists/agent-layer-health-check.md',
    'system/maintenance/checklists/query-agent-behavior-check.md',
    'system/maintenance/checklists/release-package-check.md',
    'system/maintenance/checklists/check-raw-depth.ps1',
    'system/maintenance/checklists/check-raw-style.ps1',
    'system/maintenance/checklists/run-query-agent-contract.ps1',
    'system/maintenance/checklists/run-release-contract.ps1',
    'system/maintenance/checklists/run-platform-contract.ps1'
)

foreach ($relative in $requiredFiles) {
    if (-not (Test-Path -LiteralPath (Join-Path $rootPath $relative))) { $failures.Add("Missing required file: $relative") }
}

$requiredDirectories = @(
    'Clippings', 'raw-sources', 'wiki', 'domains',
    'agents', 'agents/prompts',
    'system', 'system/protocols', 'system/registry', 'system/integrations',
    'system/maintenance', 'system/maintenance/CHANGELOG_archive', 'system/maintenance/checklists'
)
$actualDirectories = @(Get-ChildItem -LiteralPath $rootPath -Recurse -Directory -Force | ForEach-Object {
    $_.FullName.Substring($rootPath.Length).TrimStart('\', '/').Replace('\', '/')
})
foreach ($relative in $requiredDirectories) {
    if ($relative -notin $actualDirectories) { $failures.Add("Missing formal directory: $relative") }
}
foreach ($relative in $actualDirectories) {
    if ($relative -notin $requiredDirectories) { $failures.Add("Unexpected directory outside formal tree: $relative") }
}

$allowedRootFiles = @('.gitignore', '_release.json', 'README.md', 'AGENTS.md', 'COMMAND_MANUAL.md', 'NOW.md')
Get-ChildItem -LiteralPath $rootPath -File -Force | Where-Object { $_.Name -notin $allowedRootFiles } | ForEach-Object {
    $failures.Add("Unexpected root file: $($_.Name)")
}
$allowedRootDirectories = @('Clippings', 'raw-sources', 'wiki', 'domains', 'agents', 'system')
Get-ChildItem -LiteralPath $rootPath -Directory -Force | Where-Object { $_.Name -notin $allowedRootDirectories } | ForEach-Object {
    $failures.Add("Unexpected root directory: $($_.Name)")
}

foreach ($removedPath in @(
    'docs',
    'system/guides',
    'system/maintenance/PLAN.md',
    'system/maintenance/knowledge-runtime-layout.md'
)) {
    if (Test-Path -LiteralPath (Join-Path $rootPath $removedPath)) { $failures.Add("Removed path returned: $removedPath") }
}

$readmeText = [IO.File]::ReadAllText((Join-Path $rootPath 'README.md'), [Text.Encoding]::UTF8)
foreach ($token in @(
    'your-knowledge-base/',
    'system/',
    'protocols/',
    'RUNTIME_ROUTING.md',
    'registry/',
    'integrations/',
    'maintenance/'
)) {
    if (-not $readmeText.Contains($token)) { $failures.Add("README.md final tree missing token: $token") }
}
foreach ($bannedTreeToken in @('guides/', 'docs/', 'PLAN.md', 'knowledge-runtime-layout.md')) {
    if ($readmeText.Contains($bannedTreeToken)) { $failures.Add("README.md final tree contains removed token: $bannedTreeToken") }
}

$allowedContentFiles = [ordered]@{
    'Clippings' = @('README.md')
    'raw-sources' = @('README.md', 'raw-source.template.md')
    'wiki' = @('README.md', 'wiki.template.md')
    'domains' = @('README.md', 'domain.template.md')
    'agents/prompts' = @('README.md', 'expert-role.template.md', 'expert-context.template.md')
}
foreach ($directory in $allowedContentFiles.Keys) {
    $path = Join-Path $rootPath $directory
    $allowed = $allowedContentFiles[$directory]
    $unexpected = @(Get-ChildItem -LiteralPath $path -File | Where-Object { $_.Name -notin $allowed })
    foreach ($file in $unexpected) { $failures.Add("Unexpected content file: $directory/$($file.Name)") }
}

$allFiles = @(Get-ChildItem -LiteralPath $rootPath -Recurse -File)
$packageFiles = @($allFiles | Where-Object {
    $_.FullName.Substring($rootPath.Length).TrimStart('\', '/').Replace('\', '/') -notin @(
        '_release.json',
        'system/integrations/ima-config.local.json'
    )
})
if ($requiredFiles.Count -ne 54) { $failures.Add("Required-file contract must contain 54 entries, found $($requiredFiles.Count)") }
if ($packageFiles.Count -ne 54) { $failures.Add("Expected 54 package files, found $($packageFiles.Count)") }
$markerPath = Join-Path $rootPath '_release.json'
try {
    $marker = Get-Content -LiteralPath $markerPath -Raw -Encoding utf8 | ConvertFrom-Json
    foreach ($field in @('release_schema', 'source_revision', 'generator_version', 'generated_at', 'manifest_sha256')) {
        if ($null -eq $marker.PSObject.Properties[$field]) { $failures.Add("Release marker missing field: $field") }
    }
    if ($marker.release_schema -ne 1) { $failures.Add('Release marker schema must be 1') }
    if ([string]$marker.source_revision -notmatch '^[0-9a-f]{40}$') { $failures.Add('Release marker source_revision is invalid') }
    if ([string]$marker.manifest_sha256 -notmatch '^[0-9a-f]{64}$') { $failures.Add('Release marker manifest_sha256 is invalid') }
    try { [void][DateTimeOffset]::Parse([string]$marker.generated_at) }
    catch { $failures.Add('Release marker generated_at is invalid') }
}
catch { $failures.Add('Invalid JSON: _release.json') }
foreach ($file in $allFiles) {
    $bytes = [IO.File]::ReadAllBytes($file.FullName)
    $hasBom = $bytes.Length -ge 3 -and $bytes[0] -eq 239 -and $bytes[1] -eq 187 -and $bytes[2] -eq 191
    if ($hasBom) { $failures.Add("UTF-8 BOM found: $($file.FullName)") }
    for ($i = 0; $i -lt $bytes.Length - 1; $i++) {
        if ($bytes[$i] -eq 13 -and $bytes[$i + 1] -eq 10) {
            $failures.Add("CRLF found: $($file.FullName)")
            break
        }
    }
}

$textFiles = @($allFiles | Where-Object { $_.Extension -in @('.md', '.ps1', '.json') -or $_.Name -eq '.gitignore' })
$sensitiveTerms = @(('Ty' + 'ler'), ('Zh' + 'ong'), ('001a3c17' + '10c06be5'), '[A-Za-z]:\\Users\\', '/(?:Users|home)/[^/\s]+/')
$sensitivePattern = '(?i)(' + ($sensitiveTerms -join '|') + ')'
foreach ($file in $textFiles) {
    $text = [IO.File]::ReadAllText($file.FullName, [Text.Encoding]::UTF8)
    if ($text -match $sensitivePattern) { $failures.Add("Sensitive value found: $($file.FullName)") }
    $relative = $file.FullName.Substring($rootPath.Length).TrimStart('\', '/').Replace('\', '/')
    if ($relative -ne 'system/maintenance/CHANGELOG.md' -and $text -match '(\.\.[\\/]Knowledge(?:[\\/]|\b))') {
        $failures.Add("Runtime parent dependency found: $relative")
    }
    if ($relative -notin @(
        'system/maintenance/CHANGELOG.md',
        'system/maintenance/checklists/run-release-contract.ps1'
    )) {
        foreach ($legacyPattern in @(
            '(?<!system/maintenance/)scripts/',
            '_checklists/',
            '_templates/',
            'docs/reference/knowledge-runtime-layout\.md',
            'docs/maintenance/README\.md',
            '(?<!system/)integrations/(?:README|IMA-GUIDE|ima-config)',
            'system/guides/',
            'system/maintenance/PLAN\.md',
            'system/maintenance/knowledge-runtime-layout\.md',
            'docs/superpowers/',
            'llm-wiki\.md'
        )) {
            if ($text -match $legacyPattern) { $failures.Add("Legacy flat-path reference found in ${relative}: $legacyPattern") }
        }
    }
}

$markdownFiles = @($allFiles | Where-Object { $_.Extension -eq '.md' })
foreach ($file in $markdownFiles) {
    $text = [IO.File]::ReadAllText($file.FullName, [Text.Encoding]::UTF8)
    $linkText = [regex]::Replace($text, '(?ms)```.*?```', '')
    $linkText = [regex]::Replace($linkText, '`[^`\r\n]+`', '')
    $matches = [regex]::Matches($linkText, '(?<!!)\[[^\]]+\]\((?<target>[^)]+)\)')
    foreach ($match in $matches) {
        $target = $match.Groups['target'].Value.Trim('<', '>')
        if ($target -match '^(https?://|mailto:|#)' -or [string]::IsNullOrWhiteSpace($target)) { continue }
        $pathPart = ($target -split '#', 2)[0]
        if ([string]::IsNullOrWhiteSpace($pathPart)) { continue }
        $resolved = Join-Path $file.DirectoryName ([Uri]::UnescapeDataString($pathPart).Replace('/', [IO.Path]::DirectorySeparatorChar))
        if (-not (Test-Path -LiteralPath $resolved)) { $failures.Add("Broken link in $($file.FullName): $target") }
    }
}

try { Get-Content -LiteralPath (Join-Path $rootPath 'system/integrations/ima-config.template.json') -Raw -Encoding utf8 | ConvertFrom-Json | Out-Null }
catch { $failures.Add('Invalid JSON: system/integrations/ima-config.template.json') }

$wizardScriptPath = Join-Path $rootPath 'system/maintenance/setup-wizard.ps1'
$wizardTextPath = Join-Path $rootPath 'system/maintenance/setup-wizard.zh-CN.json'
try { $wizardText = Get-Content -LiteralPath $wizardTextPath -Raw -Encoding utf8 | ConvertFrom-Json }
catch { $failures.Add('Invalid JSON: system/maintenance/setup-wizard.zh-CN.json') }

if (Test-Path -LiteralPath $wizardScriptPath) {
    $wizardScript = [IO.File]::ReadAllText($wizardScriptPath, [Text.Encoding]::UTF8)
    if ($wizardScript -match '[^\x00-\x7F]') { $failures.Add('Wizard PowerShell must stay ASCII for Windows PowerShell 5.1.') }
    foreach ($token in @('Read-Host', 'AnswerFile', 'initialize-knowledge.ps1', 'Invoke-Initializer')) {
        if (-not $wizardScript.Contains($token)) { $failures.Add("Wizard script missing token: $token") }
    }
    $parseTokens = $null
    $parseErrors = $null
    [void][System.Management.Automation.Language.Parser]::ParseFile($wizardScriptPath, [ref]$parseTokens, [ref]$parseErrors)
    foreach ($parseError in @($parseErrors)) { $failures.Add("Wizard parse error: $($parseError.Message)") }
}

if ($null -ne $wizardText) {
    foreach ($key in @('display_name', 'directory_name', 'purpose', 'audience', 'topics', 'ima', 'advanced', 'confirm')) {
        if ($null -eq $wizardText.questions.PSObject.Properties[$key]) { $failures.Add("Wizard localization missing question: $key") }
    }
    foreach ($control in @('?', 'B', 'S', 'Q')) {
        if (-not $wizardText.labels.controls.Contains($control)) { $failures.Add("Wizard localization missing control: $control") }
    }
}

if ($failures.Count -gt 0) {
    $failures | Sort-Object -Unique | ForEach-Object { Write-Error $_ }
    exit 1
}

& (Join-Path $rootPath 'system/maintenance/checklists/check-raw-depth.ps1') -Root $rootPath
& (Join-Path $rootPath 'system/maintenance/checklists/check-raw-style.ps1') -Root $rootPath
& (Join-Path $rootPath 'system/maintenance/checklists/run-query-agent-contract.ps1') -Root $rootPath
& (Join-Path $rootPath 'system/maintenance/checklists/run-platform-contract.ps1') -Root $rootPath
Write-Output "Release contract: PASS ($($packageFiles.Count) business files; $($allFiles.Count) versioned runtime files)"
