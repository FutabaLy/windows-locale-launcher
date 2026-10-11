# Windows Locale Launcher Skill

为原生 **32 位 Windows 日文游戏**制作双击启动的免手动转区启动器。启动器使用便携 Locale Emulator，为目标进程模拟日文 CP932 环境，无需玩家安装右键菜单或修改 Windows 系统区域。

这是提供给 Codex 等可读写本地文件、执行脚本的助手使用的技能，不是通用游戏汉化器。它不翻译剧情、不处理认证，也不支持任意 64 位或 .NET 游戏。

## 安装技能

向 Codex 发送：

```text
帮我安装 skill https://github.com/FutabaLy/windows-locale-launcher
```

也可以将仓库完整下载到 Codex 的个人技能目录，保留 `SKILL.md`、`scripts`、`assets` 和 `references`。

## 使用教程：复制一句话即可

安装技能后，把下面的指令发送给 Codex。将方括号内的示例路径替换成你的实际路径，方括号可以去掉。需要使用能够访问本地游戏文件的 Codex，普通网页聊天不能直接操作电脑里的游戏。

### 1. 制作并放回游戏目录

提供**游戏启动 EXE 的完整路径**，例如：

```text
请使用 windows-locale-launcher，帮我给这个游戏制作免手动转区启动补丁，并放回游戏目录：[E:\Games\ママトモ\Start.exe]。保留原有汉化、存档和游戏文件，让我以后双击新启动器就能游玩。
```

如果不知道哪个 EXE 是启动程序，也可以提供游戏文件夹：

```text
请使用 windows-locale-launcher，帮我检查这个游戏目录：[E:\Games\ママトモ]。确认启动程序和兼容性后，制作免手动转区启动器并放回游戏目录。
```

助手会检查程序位数、已有汉化和区域配置，下载所需官方运行组件，构建独立启动器，并验证文件及区域模拟环境。遇到不支持的程序类型时，会说明原因。

### 2. 双击新启动器

制作并部署后，游戏目录大致如下，具体名称以助手交付为准：

```text
游戏目录/
├─ Start.exe                 原游戏启动程序
├─ 游戏一键启动.exe          以后双击这个文件
└─ LocaleLauncherRuntime/    配套运行组件，需要保留
```

不需要再右键选择转区，也不需要另外安装 Locale Emulator。**不要只复制启动器 EXE，配套文件夹需要一起保留。** 移动整个游戏目录后仍可使用。

启动后检查文字、剧情选项和存读档。文件检查及代码页测试通过，不代表助手已替你完成游戏内测试。

### 3. 出现问题时继续让助手检查

```text
请使用 windows-locale-launcher，检查这个启动器的问题：[E:\Games\ママトモ\游戏一键启动.exe]。现象是：[填写报错、闪退或乱码情况]。请读取启动日志，保留现有存档和汉化后排查。
```

有报错窗口时可以同时附上截图，日志通常位于配套目录的 `launcher-check.txt`。

### 只制作补丁包，暂时不放回游戏

```text
请使用 windows-locale-launcher，为这个游戏制作免手动转区启动补丁包：[E:\Games\ママトモ\Start.exe]。只生成补丁包和使用说明，暂时不要部署到游戏目录。
```

恢复原来的启动方式时，只需删除本次新增的启动器和配套目录，保留原游戏文件即可。

## 软件与依赖

- **制作端**：Windows、Python 3.11+、.NET Framework C# 编译器。原生代码页探针测试另需可生成 x86 程序的 C 工具链。
- **技能本身**不附带转区工具二进制；构建时从 [Locale Emulator 官方发布页](https://github.com/xupefei/Locale-Emulator/releases/tag/v2.5.0.1)获取指定 ZIP，脚本核对 SHA-256。
- **生成的启动包**包含所需便携运行组件，玩家无需另行安装 Locale Emulator。启动器依赖 Windows .NET Framework 4.x。
- 不会自动安装全局右键扩展、修改系统区域或运行用户游戏。

## 手动构建

先下载 `Locale.Emulator.2.5.0.1.zip`，然后执行：

```powershell
python scripts/build_launcher.py --game-exe "X:\Game\Start.exe" --runtime-zip "X:\Downloads\Locale.Emulator.2.5.0.1.zip" --output "X:\Build\NewLauncher" --name "游戏一键启动.exe"
```

输出目录必须不存在。构建命令不部署、不启动游戏；生成包须与目标 EXE 放在同一目录。`--check` 仅检查文件与配置。完整流程见 [SKILL.md](SKILL.md)，运行环境验证见 [验证与排错](references/verification.md)。

## 验证范围

通用构建脚本已通过原生 x86 探针的端到端测试：生成的启动器能够提供 CP932 环境；文件检查、非法文件名拒绝和 CLR 目标拒绝亦已验证。不同游戏、Windows 版本、字体补丁及存档路径仍需分别测试。

“免手动转区”指自动进行进程级区域模拟，并不表示游戏已被改写为原生 Unicode 程序。文件检查或代码页探针成功，不等于整部游戏运行已验证。

## 第三方来源

运行组件来自 [Locale Emulator](https://github.com/xupefei/Locale-Emulator) 及其 [Core](https://github.com/xupefei/Locale-Emulator-Core)。`LECommonLibrary.dll` 从固定哈希官方安装器的资源中提取，构建时不运行安装器。

随附的 [COPYING](assets/COPYING) 和 [COPYING.LESSER](assets/COPYING.LESSER) 是上游许可证文本，并随生成的启动包分发。本仓库不包含游戏程序、剧本、存档或其他商业游戏资源。
