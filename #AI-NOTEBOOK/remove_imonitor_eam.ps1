#remove_imonitor_eam.ps1
#iMonitor EAM 员工监控软件通用清除脚本
#使用方法：以管理员身份运行 PowerShell，执行：
#   Set-ExecutionPolicy Bypass -Scope Process -Force
#   & "脚本路径\remove_imonitor_eam.ps1"
#
#可选参数：
#   -InstallPath "自定义安装路径"  （默认自动检测）

param(
    [string]$InstallPath = ""
)

# ===== 前置检查 =====
$ErrorActionPreference = 'Continue'
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "[ERROR] 需要管理员权限！请右键 PowerShell -> 以管理员身份运行" -ForegroundColor Red
    Write-Host ""
    Write-Host "按任意键退出..."
    $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
    exit 1
}

$ts = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
$tempDir = $env:TEMP
$log = @()
$log += "============================================"
$log += "  iMonitor EAM Removal Script"
$log += "  Started: $ts"
$log += "  User: $env:USERNAME"
$log += "============================================"
$log += ""

# ===== 配置 =====
$targetProcesses = @(
    'eamusbsrv64','eamusbsrv','eamplay','ProcGuard','msflttrans',
    'mskes','msptr','mstme','mdua','EnumDev','EnumProcessPort',
    'Fport','Combine','devcon','uninstallmsfilter'
)

$targetServices = @('WinUsbAutoSrv','imonagent')

$targetDrivers = @('msfilter','msflt','ProcGuard','eamflt','eamguard','eammon')

# 精确匹配模式（避免误伤 Teams 等软件）
$regPattern = 'syscon|eamplay|eamusbsrv|mdua|msfilter|ProcGuard|mskes|msptr|mstme|WinUsbAutoSrv|imonagent|eam_strings|agentsettings'

# 自动检测安装路径
$defaultPath = 'C:\Windows\System\sys\syscon'
$settingsPath = 'C:\Windows\System\sys\syssettings'
$parentPath = 'C:\Windows\System\sys'

if ($InstallPath -ne "") {
    $defaultPath = $InstallPath
    $parentPath = Split-Path $InstallPath -Parent
    $settingsPath = Join-Path $parentPath "syssettings"
}

$log += "Target paths:"
$log += "  Main:      $defaultPath"
$log += "  Settings:  $settingsPath"
$log += "  Parent:    $parentPath"
$log += ""

# ===== Step 1: 备份取证 =====
$log += "========== STEP 1: Backup =========="
$backupBase = Join-Path $tempDir "imonitor_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"

$dirsToBackup = @()
if (Test-Path $defaultPath) { $dirsToBackup += @{Src=$defaultPath; Name='syscon'} }
if (Test-Path $settingsPath) { $dirsToBackup += @{Src=$settingsPath; Name='syssettings'} }

if ($dirsToBackup.Count -gt 0) {
    New-Item -ItemType Directory -Path $backupBase -Force | Out-Null
    foreach ($dir in $dirsToBackup) {
        try {
            $dest = Join-Path $backupBase $dir.Name
            Copy-Item -Path $dir.Src -Destination $dest -Recurse -Force -ErrorAction Stop
            $fileCount = (Get-ChildItem $dest -Recurse -File -ErrorAction SilentlyContinue).Count
            $log += "  [OK] Backed up $($dir.Name): $fileCount files -> $dest"
        } catch {
            $log += "  [WARN] Backup failed for $($dir.Name): $($_.Exception.Message)"
        }
    }
    $log += "  Backup location: $backupBase"
} else {
    $log += "  [SKIP] No directories found to backup"
}
$log += ""

# ===== Step 2: 终止进程 =====
$log += "========== STEP 2: Kill Processes =========="
foreach ($name in $targetProcesses) {
    $procs = Get-Process -Name $name -ErrorAction SilentlyContinue
    if ($procs) {
        foreach ($p in $procs) {
            $log += "  Killing: $($p.ProcessName) (PID: $($p.Id))"
            & taskkill.exe /F /PID $p.Id 2>&1 | ForEach-Object { $log += "    -> $_" }
        }
    }
}
Start-Sleep -Seconds 2

# Verify
$stillRunning = Get-Process -ErrorAction SilentlyContinue | Where-Object { $targetProcesses -contains $_.ProcessName }
if ($stillRunning) {
    $log += "  [WARN] Still running (may be protected by ProcGuard):"
    foreach ($p in $stillRunning) { $log += "    -> $($p.ProcessName) (PID: $($p.Id))" }
    $log += "  -> Will continue, service+file removal + reboot will clear them"
} else {
    $log += "  [OK] All monitoring processes terminated"
}
$log += ""

# ===== Step 3: 停止服务 =====
$log += "========== STEP 3: Stop Services =========="
foreach ($svc in $targetServices) {
    $s = Get-Service -Name $svc -ErrorAction SilentlyContinue
    if ($s) {
        $log += "  Stopping: $svc (Status: $($s.Status))"
        & sc.exe stop $svc 2>&1 | ForEach-Object { $log += "    -> $_" }
    } else {
        $log += "  [SKIP] Service not found: $svc"
    }
}
Start-Sleep -Seconds 1
$log += ""

# ===== Step 4: 禁用服务 =====
$log += "========== STEP 4: Disable Services =========="
foreach ($svc in $targetServices) {
    $s = Get-Service -Name $svc -ErrorAction SilentlyContinue
    if ($s) {
        & sc.exe config $svc start= disabled 2>&1 | ForEach-Object { $log += "  $svc -> $_" }
    }
}
$log += ""

# ===== Step 5: 删除服务 =====
$log += "========== STEP 5: Delete Services =========="
foreach ($svc in $targetServices) {
    $s = Get-Service -Name $svc -ErrorAction SilentlyContinue
    if ($s) {
        & sc.exe delete $svc 2>&1 | ForEach-Object { $log += "  $svc -> $_" }
    } else {
        $log += "  [SKIP] Service not found: $svc"
    }
}
$log += ""

# ===== Step 6: 清除注册表启动项 =====
$log += "========== STEP 6: Clean Registry Startup =========="
$regPaths = @(
    'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run',
    'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce',
    'HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Run',
    'HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\RunOnce',
    'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run',
    'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce'
)
foreach ($rp in $regPaths) {
    if (Test-Path $rp) {
        $props = Get-ItemProperty -Path $rp -ErrorAction SilentlyContinue
        if ($props) {
            $props.PSObject.Properties | Where-Object {
                $_.Name -notmatch '^PS' -and $_.Value -match $regPattern
            } | ForEach-Object {
                $log += "  Found: $($_.Name) = $($_.Value)"
                $log += "    in: $rp"
                try {
                    Remove-ItemProperty -Path $rp -Name $_.Name -Force -ErrorAction Stop
                    $log += "    -> [OK] REMOVED"
                } catch {
                    $log += "    -> [WARN] Remove failed: $($_.Exception.Message)"
                }
            }
        }
    }
}

# Check Winlogon
$winlogon = Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon' -ErrorAction SilentlyContinue
if ($winlogon.Userinit -match $regPattern) {
    $log += "  [WARN] Winlogon Userinit contains monitoring ref: $($winlogon.Userinit)"
    $log += "  -> Manual fix required: check HKLM\...\Winlogon\Userinit"
}
$log += ""

# ===== Step 7: 删除服务注册表项 =====
$log += "========== STEP 7: Delete Service Registry =========="
foreach ($svc in $targetServices) {
    $svcRegPath = "HKLM:\SYSTEM\CurrentControlSet\Services\$svc"
    if (Test-Path $svcRegPath) {
        try {
            Remove-Item -Path $svcRegPath -Recurse -Force -ErrorAction Stop
            $log += "  [OK] Deleted: $svcRegPath"
        } catch {
            $log += "  [WARN] Delete failed: $($_.Exception.Message)"
            & reg.exe delete "HKLM\SYSTEM\CurrentControlSet\Services\$svc" /f 2>&1 | ForEach-Object { $log += "    reg: $_" }
        }
    } else {
        $log += "  [SKIP] Not found: $svcRegPath"
    }
}
$log += ""

# ===== Step 8: 清除内核驱动 =====
$log += "========== STEP 8: Remove Kernel Drivers =========="
foreach ($drv in $targetDrivers) {
    $drvPath = "HKLM:\SYSTEM\CurrentControlSet\Services\$drv"
    if (Test-Path $drvPath) {
        $log += "  Found driver: $drv"
        & sc.exe stop $drv 2>&1 | ForEach-Object { $log += "    stop: $_" }
        & sc.exe delete $drv 2>&1 | ForEach-Object { $log += "    delete: $_" }
    }
}

# Check for .sys files in install dir
if (Test-Path $defaultPath) {
    $sysFiles = Get-ChildItem "$defaultPath\*.sys" -ErrorAction SilentlyContinue
    if ($sysFiles) {
        foreach ($f in $sysFiles) { $log += "  Found .sys: $($f.Name)" }
    }
}
$log += ""

# ===== Step 9: 清除计划任务 =====
$log += "========== STEP 9: Clean Scheduled Tasks =========="
$schTasks = Get-ScheduledTask -ErrorAction SilentlyContinue | Where-Object {
    $_.Actions.Execute -match $regPattern -or
    $_.TaskName -match $regPattern
}
if ($schTasks) {
    foreach ($t in $schTasks) {
        $log += "  Found: $($t.TaskName)"
        try {
            Unregister-ScheduledTask -TaskName $t.TaskName -TaskPath $t.TaskPath -Confirm:$false -ErrorAction Stop
            $log += "    -> [OK] DELETED"
        } catch {
            $log += "    -> [WARN] Delete failed: $($_.Exception.Message)"
        }
    }
} else {
    $log += "  [OK] No suspicious scheduled tasks"
}
$log += ""

# ===== Step 10: 接管权限并删除文件 =====
$log += "========== STEP 10: Take Ownership & Delete Files =========="

$dirsToDelete = @()
if (Test-Path $defaultPath) { $dirsToDelete += $defaultPath }
if (Test-Path $settingsPath) { $dirsToDelete += $settingsPath }
if (Test-Path $parentPath) { $dirsToDelete += $parentPath }

# Deduplicate
$dirsToDelete = $dirsToDelete | Sort-Object -Unique

foreach ($dir in $dirsToDelete) {
    if (Test-Path $dir) {
        $log += "  Processing: $dir"

        # Take ownership
        & takeown.exe /F $dir /R /D Y 2>&1 | Select-Object -Last 1 | ForEach-Object { $log += "    takeown: $_" }

        # Grant full control
        & icacls.exe $dir /grant administrators:F /T /C 2>&1 | Select-Object -Last 1 | ForEach-Object { $log += "    icacls: $_" }

        # Delete
        try {
            Remove-Item -Path $dir -Recurse -Force -ErrorAction Stop
            $log += "    -> [OK] DELETED"
        } catch {
            $log += "    -> PowerShell delete failed, trying cmd..."
            & cmd.exe /c "rd /s /q `"$dir`"" 2>&1 | ForEach-Object { $log += "      cmd: $_" }
            if (-not (Test-Path $dir)) {
                $log += "    -> [OK] DELETED via cmd"
            } else {
                $log += "    -> [WARN] Directory still exists, will be cleared after reboot"
            }
        }
    }
}
$log += ""

# ===== 最终验证 =====
$log += "========== FINAL VERIFICATION =========="

# Processes
$procCheck = Get-Process -ErrorAction SilentlyContinue | Where-Object { $targetProcesses -contains $_.ProcessName }
if ($procCheck) {
    $log += "[FAIL] Processes still running:"
    foreach ($p in $procCheck) { $log += "  -> $($p.ProcessName) (PID: $($p.Id))" }
} else {
    $log += "[OK] No monitoring processes running"
}

# Services
foreach ($svc in $targetServices) {
    $s = Get-Service -Name $svc -ErrorAction SilentlyContinue
    if ($s) {
        $log += "[FAIL] Service still exists: $svc ($($s.Status))"
    } else {
        $log += "[OK] Service removed: $svc"
    }
}

# Directories
foreach ($dir in @($defaultPath, $settingsPath, $parentPath)) {
    if (Test-Path $dir) {
        $remaining = (Get-ChildItem $dir -Recurse -Force -ErrorAction SilentlyContinue).Count
        $log += "[FAIL] Directory exists with $remaining files: $dir"
    } else {
        $log += "[OK] Directory removed: $dir"
    }
}

# Prefetch (historical execution check)
$prefetchCheck = Get-ChildItem 'C:\Windows\Prefetch' -ErrorAction SilentlyContinue | Where-Object {
    $_.Name -match 'EAMPLAY|MSKES|MSPTR|MSTME|MDUA|MSFLTTRANS|PROCGUARD'
}
if ($prefetchCheck) {
    $log += "[INFO] Prefetch records found (historical execution evidence):"
    foreach ($pf in $prefetchCheck) { $log += "  -> $($pf.Name)" }
} else {
    $log += "[OK] No Prefetch records - monitoring agents were never executed"
}

$log += ""
$log += "============================================"
$log += "  Script completed: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
$log += "  Backup at: $backupBase"
$log += "  Log file: $tempDir\imonitor_removal_result.txt"
if ($procCheck -or (Get-Service -Name 'WinUsbAutoSrv' -ErrorAction SilentlyContinue) -or (Test-Path $defaultPath)) {
    $log += ""
    $log += "  [ACTION NEEDED] Some items remain. Please REBOOT your computer"
    $log += "  and re-run this script to complete cleanup."
}
$log += "============================================"

# Write log file
$resultFile = Join-Path $tempDir "imonitor_removal_result.txt"
$log | Out-File -FilePath $resultFile -Encoding UTF8

# Print to console
foreach ($line in $log) { Write-Host $line }

Write-Host ""
Write-Host "Log saved to: $resultFile" -ForegroundColor Cyan
Write-Host "Backup saved to: $backupBase" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
