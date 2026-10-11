# 构建验证与故障定位

## 三层验证

1. **文件检查**：在任务工作目录建临时布局，复制构建包和用户目标 EXE（只复制、不运行）；通过 `Start-Process -WindowStyle Hidden -Wait -PassThru` 运行启动器 `--check`，检查 ExitCode 与 `launcher-check.txt`。目标 EXE 不是启动器本身，路径和 GUID 应吻合。
2. **区域模拟**：用自建的原生 x86 小程序调用 `GetACP` 并写入本地报告。先在普通环境运行记录基线，再使用包内 `LEProc.exe -runas <build-manifest 中的 profile_guid> "<探针绝对路径>"` 运行。设置明确工作目录，检查报告本次更新时间和 ACP=932，防止读到旧文件。构建脚本不自动做这一步。
3. **游戏运行**：得到已有用户授权后启动游戏，确认画面、文本、选项和存读档。若只交付补丁，则由用户运行反馈，不声称已经完整实测。

检查阶段使用 `--check`，不要只启动 EXE 误打开游戏。运行后台辅助进程使用隐藏窗口；用户要看的游戏窗口另行处理。针对游戏原件，部署与启动分别判断授权范围。

## 纯原生探针

随包 `assets/Probe.c` 不依赖 CRT。使用可用的 x86 C 编译器；不要下载来源不明的探针。

若本机只有 x64 MinGW 但工具支持生成 i386，可用如下例子在工作目录构建（按实际工具绝对路径运行）：

```text
dlltool -m i386 -f --32 -k -d <skill>/assets/kernel32.def -l <work>/kernel32-x86.a
gcc -m32 -Os -fno-stack-protector -c <skill>/assets/Probe.c -o <work>/Probe.o
ld -mi386pe --subsystem console -e _mainCRTStartup -o <work>/NativeProbe.exe <work>/Probe.o <work>/kernel32-x86.a
```

探针将 `native-probe.txt` 写到进程当前目录。LEProc 默认把当前目录设为目标 EXE 所在目录，因此普通基线也应使用这个目录。测试前记录或换名旧报告。不要将探针当成游戏一起部署。

在原生 x86 测试通过后，如需端到端验证启动器，可用探针做 `--game-exe` 构建单独测试包，再把探针放入该包模拟游戏布局。双击/运行启动器，检查新报告；这不会运行用户游戏。

## 已知排错线索

- **缺少 LECommonLibrary.dll**：2.5.0.1 ZIP 没有直接列出它，官方 `LEInstaller.exe` 把它嵌在 `LEInstaller.Properties.Resources.resources` 的 `LECommonLibrary` 项。本脚本从固定哈希官方包提取。不要因此安装全局右键菜单，也不要换用其他游戏的 DLL。
- **LEProc 立即退出或 .NET 异常**：检查完整依赖及真实退出码；`Start-Process` 调用成功不等于子进程成功。先核对公共 DLL，不急着更换系统设置。
- **托管探针仍显示 ACP936**：托管 CLR 运行路径不能作为原生游戏的等价测试；改用原生探针。不要直接承诺所有 .NET/64 位目标可运行。
- **原生探针不通过**：核对位数、配套 DLL、配置解析、工作目录和实际日志。若沙盒隔离可能影响进程级模拟，可按环境要求申请在正常用户环境运行自建探针；不得绕过拒绝或停用安全软件。
- **已有配置 zh-HK 与剧本 CP932 不一致**：保留原配置，确认当前可用方式与真实文本编码；显式 `-runas` 使用独立配置以免被目标 `.le.config` 覆盖。用户确认需要其他区域时，应修改构建方案及测试预期，不能仅换配置后沿用 CP932 成功声明。
- **路径或存档问题**：检查 ANSI 路径能否表示中文目录，以及游戏实际读取位置；仅在授权的新副本测试 ASCII 路径，不移动原游戏或覆盖存档来试错。

## 来源

- 发布包：https://github.com/xupefei/Locale-Emulator/releases/tag/v2.5.0.1
- 命令行：https://github.com/xupefei/Locale-Emulator/blob/v2.5.0.1/LEProc/Program.cs
- 配置：https://github.com/xupefei/Locale-Emulator/blob/v2.5.0.1/LECommonLibrary/LEConfig.cs
- 核心实现：https://github.com/xupefei/Locale-Emulator-Core

固定版本是已验证构建基线，不声称它兼容每个新版 Windows。更换版本时更新来源、依赖、哈希及实际测试，不能静默放宽校验。
