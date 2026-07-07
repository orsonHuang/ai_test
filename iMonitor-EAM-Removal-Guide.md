# iMonitor EAM 监控软件清除指南

> 适用于在个人电脑上发现未经授权安装的 iMonitor EAM（Employee Activity Monitoring）员工监控软件时的完整清除流程。

---

## 一、软件特征识别

### 典型安装路径

| 路径 | 用途 |
|------|------|
| `C:\Windows\System\sys\syscon` | 主程序目录（62+ 个文件） |
| `C:\Windows\System\sys\syssettings` | 配置目录（服务器IP、账号等） |

### 伪装手段

| 伪装项 | 实际身份 |
|--------|----------|
| 目录名 `System\sys\syscon` | 伪装成 Windows 系统目录 |
| 服务名 `WinUsbAutoSrv` | 伪装成 Windows USB 自动服务 |
| 备用服务名 `imonagent` | 备用持久化入口 |
| 进程名 `ms` 前缀（mskes/msptr/mstme/mswe） | 伪装成微软产品 |
| 注册表启动项 `mdua` | 伪装成系统组件 |

### 核心进程清单

| 进程名 | 功能 |
|--------|------|
| `eamusbsrv64.exe` / `eamusbsrv.exe` | USB 监控服务（常驻） |
| `eamplay.exe` | 主监控代理（截屏/键盘记录/网页/聊天） |
| `ProcGuard.exe` | 进程保护器（阻止杀进程） |
| `msflttrans.exe` | 文件过滤驱动传输 |
| `mskes.exe` | 键盘记录引擎 |
| `msptr.exe` | 打印监控 |
| `mstme.exe` | 时间/应用统计 |
| `mdua.exe` | 自启动代理 |
| `EnumDev.exe` / `EnumProcessPort.exe` | 设备/端口枚举 |
| `Fport.exe` | 端口映射工具 |
| `Combine.exe` | 截图合成工具 |
| `devcon.exe` | 设备控制工具 |
| `uninstallmsfilter.exe` | 卸载程序 |

### 关键 DLL（注入用）

`EasyHook32.dll`、`NtHookEngine.dll`、`ProcMonInject.dll`、`MSWordAddin.dll`、`MSWordAddin64.dll`

---

## 二、清除流程（共 4 步）

### 第 1 步：下载清除脚本

将 `remove_imonitor_eam.ps1`（见附件）保存到电脑任意位置，例如桌面。

### 第 2 步：以管理员身份运行

1. 按 `Win + X`，选择 **"终端(管理员)"** 或 **"Windows PowerShell(管理员)"**
2. 在 UAC 弹窗中点击 **"是"**
3. 执行脚本：

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force
& "脚本保存的完整路径\remove_imonitor_eam.ps1"
```

例如脚本放在桌面：
```powershell
& "$env:USERPROFILE\Desktop\remove_imonitor_eam.ps1"
```

### 第 3 步：重启电脑

重启确保所有更改生效，防止残留进程重新拉起。

### 第 4 步：验证清除结果

脚本执行完毕后会自动输出验证结果。也可手动检查：

```powershell
# 检查进程
Get-Process | Where-Object { 'eamusbsrv64','eamusbsrv','eamplay','ProcGuard','msflttrans','mskes','msptr','mstme','mdua' -contains $_.ProcessName }

# 检查服务
Get-Service -Name 'WinUsbAutoSrv','imonagent' -ErrorAction SilentlyContinue

# 检查目录
Test-Path 'C:\Windows\System\sys'

# 检查注册表
Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run' -ErrorAction SilentlyContinue | Select-Object mdua
```

以上全部返回空或 `False` 即表示清除成功。

---

## 三、脚本自动执行的 10 个步骤

| 步骤 | 操作 | 说明 |
|------|------|------|
| 1 | 备份取证 | 将 `syscon` 和 `syssettings` 目录完整复制到 Temp 作为证据保留 |
| 2 | 终止进程 | 强制终止所有监控相关进程（15 个进程名） |
| 3 | 停止服务 | `sc stop WinUsbAutoSrv` + `sc stop imonagent` |
| 4 | 禁用服务 | `sc config ... start= disabled` |
| 5 | 删除服务 | `sc delete ...`（彻底移除服务注册） |
| 6 | 清除注册表启动项 | 扫描 6 个 Run/RunOnce 键，移除所有匹配项 |
| 7 | 清除注册表服务项 | 删除 `HKLM\SYSTEM\...\Services\WinUsbAutoSrv` 等注册表项 |
| 8 | 清除内核驱动 | 检查并删除 msfilter/msflt/ProcGuard 等驱动注册 |
| 9 | 清除计划任务 | 扫描并删除所有监控相关计划任务 |
| 10 | 接管权限并删除文件 | `takeown` + `icacls` 接管后删除整个 `C:\Windows\System\sys` 目录 |

---

## 四、通用化调整说明

相比本次清除使用的原始脚本，通用版做了以下调整：

| 调整项 | 原始版本 | 通用版本 |
|--------|----------|----------|
| 备份路径 | 硬编码 `C:\Users\admin\...` | 使用 `$env:TEMP` 动态获取 |
| 日志路径 | 硬编码用户名 | 使用 `$env:TEMP` 动态获取 |
| syssettings 清理 | 遗漏（第二轮才补） | 合并到一个脚本中 |
| imonagent 服务 | 遗漏 | 已加入检查列表 |
| 注册表匹配模式 | `eam`（误伤 Teams） | 改为精确匹配 `eamplay\|eamusbsrv\|syscon\|mdua` 等 |
| 安装路径检测 | 硬编码 | 自动检测 + 支持自定义路径参数 |
| 验证步骤 | 基础检查 | 增加 Prefetch 检查和全目录扫描 |
| 执行方式 | 分两个脚本 | 单一脚本一次完成 |

---

## 五、注意事项

1. **必须以管理员身份运行**：普通权限无法操作系统服务和 `C:\Windows` 下的文件
2. **ProcGuard 保护**：如果 `ProcGuard.exe` 正在运行，它会阻止杀进程。脚本会先尝试终止，失败则继续执行后续步骤——删除服务 + 文件后重启即可
3. **备份保留**：清除前会自动备份到 `%TEMP%` 目录，建议确认备份成功后再删除原始文件
4. **误伤风险**：通用版已修复注册表匹配模式，不会误删其他软件的启动项
5. **网络隔离**：如果监控服务器在内网（如 `172.16.x.x`），脱离该网络后软件无法外传数据，但仍建议清除
6. **取证用途**：如果需要法律维权，备份文件中的 `config.ini` 和 `serverip.cfg` 包含服务器 IP 和管理账号信息

---

## 六、隐私影响评估

清除后可通过备份文件中的 `agentsettings.cfg` 评估实际隐私影响：

- **`enable_snapshots=1` + `eamplay.exe` 在 Prefetch 中有记录** → 截屏功能曾实际运行
- **`enable_snapshots=1` + `eamplay.exe` 在 Prefetch 中无记录** → 截屏配置开启但从未运行
- **`sync_server` 为空** → 即使收集了数据也无处发送
- **`file_disableusb=1`** → USB 文件操作被禁用（唯一由 eamusbsrv64 实际执行的限制）

检查 Prefetch 记录：
```powershell
Get-ChildItem 'C:\Windows\Prefetch' -Filter '*EAMPLAY*' -ErrorAction SilentlyContinue
Get-ChildItem 'C:\Windows\Prefetch' -Filter '*MSKES*' -ErrorAction SilentlyContinue
```

无结果 = 从未运行过。
