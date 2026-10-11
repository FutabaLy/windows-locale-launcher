"""Build a portable x86 Japanese locale launcher. Does not deploy or run games."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
import uuid
import xml.etree.ElementTree as ET
import zipfile

ARCHIVE_SHA256 = '808ff584426d52cc775ad6406da00622f454be95bd4c8fbca42eef4b7235ad5c'
SKILL = Path(__file__).resolve().parents[1]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def filename(value):
    if (not value or any(c in value for c in '<>:"/\\|?*')
            or any(ord(c)<32 for c in value) or value.endswith((' ', '.'))
            or value.split('.')[0].upper() in {'CON','PRN','AUX','NUL',*(f'COM{i}' for i in range(10)),*(f'LPT{i}' for i in range(10))}):
        raise ValueError('Invalid Windows filename: '+value)
    return value

def native_x86(path):
    with path.open('rb') as f:
        head=f.read(64)
        if len(head)!=64 or head[:2]!=b'MZ': raise ValueError('Invalid PE file')
        off=struct.unpack_from('<I',head,60)[0]
        if off > path.stat().st_size-248: raise ValueError('Invalid PE offset')
        f.seek(off); pe=f.read(248)
    if pe[:4]!=b'PE\0\0' or struct.unpack_from('<H',pe,4)[0]!=0x14c or struct.unpack_from('<H',pe,24)[0]!=0x10b:
        raise ValueError('Requires x86 PE32; x64 is unsupported')
    if struct.unpack_from('<I',pe,24+92)[0] > 14 and struct.unpack_from('<I',pe,24+96+14*8)[0]:
        raise ValueError('CLR target detected; native-game workflow is not applicable')

def run(cmd):
    subprocess.run([str(x) for x in cmd],check=True,timeout=60)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--game-exe',type=Path,required=True)
    ap.add_argument('--runtime-zip',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--name',default='游戏一键启动.exe')
    ap.add_argument('--support-dir',default='LocaleLauncherRuntime')
    ap.add_argument('--csc',type=Path)
    a=ap.parse_args()
    if os.name!='nt': raise ValueError('Build on Windows')
    game=a.game_exe.resolve(strict=True); native_x86(game)
    name=filename(a.name); support=filename(a.support_dir); filename(game.name)
    if not name.lower().endswith('.exe') or len({name.casefold(),support.casefold(),game.name.casefold(),'启动说明.txt'})!=4:
        raise ValueError('Launcher, target and support names must be distinct; launcher must end in .exe')
    out=a.output.absolute()
    if out.exists(): raise FileExistsError('Use a new output directory')
    if sha(a.runtime_zip)!=ARCHIVE_SHA256: raise ValueError('Official ZIP SHA-256 mismatch')
    csc=a.csc or Path(os.environ.get('WINDIR',r'C:\Windows'))/'Microsoft.NET/Framework/v4.0.30319/csc.exe'
    if not csc.is_file(): raise FileNotFoundError('C# compiler unavailable; pass --csc')
    out.parent.mkdir(parents=True,exist_ok=True)
    before=sha(game)
    with tempfile.TemporaryDirectory(prefix='locale-build-',dir=out.parent) as temp:
        temp=Path(temp); package=temp/'package'; runtime=package/support
        runtime.mkdir(parents=True)
        with zipfile.ZipFile(a.runtime_zip) as archive:
            for member in ['LEProc.exe','LEVersion.xml','LoaderDll.dll','LocaleEmulator.dll','LEInstaller.exe']:
                info=archive.getinfo(member)
                if info.file_size > 4<<20: raise ValueError('Unexpected member size')
                dest=temp/member if member=='LEInstaller.exe' else runtime/member
                dest.write_bytes(archive.read(info))
        extractor=temp/'ExtractCommon.exe'
        run([csc,'/nologo','/platform:x86','/out:'+str(extractor),SKILL/'assets/ExtractCommon.cs'])
        run([extractor,temp/'LEInstaller.exe',runtime/'LECommonLibrary.dll'])
        guid=str(uuid.uuid4())
        config=ET.Element('LEConfig'); profiles=ET.SubElement(config,'Profiles')
        profile=ET.SubElement(profiles,'Profile',Name='Japanese CP932',Guid=guid,MainMenu='false')
        for key,value in {'Parameter':'','Location':'ja-JP','Timezone':'Tokyo Standard Time','RunAsAdmin':'false','RedirectRegistry':'true','IsAdvancedRedirection':'false','RunWithSuspend':'false'}.items():
            ET.SubElement(profile,key).text=value
        ET.ElementTree(config).write(runtime/'LEConfig.xml',encoding='utf-8',xml_declaration=True)
        source=(SKILL/'assets/Launcher.cs.template').read_text(encoding='utf-8')
        for token,value in {'TITLE':Path(name).stem,'TARGET':game.name,'SUPPORT':support,'GUID':guid}.items():
            source=source.replace('@@'+token+'@@',json.dumps(value,ensure_ascii=True))
        cs=runtime/'Launcher.cs'; cs.write_text(source,encoding='utf-8-sig')
        run([csc,'/nologo','/target:winexe','/platform:x86','/r:System.Windows.Forms.dll','/r:System.Xml.Linq.dll','/out:'+str(package/name),cs])
        for license_name in ['COPYING','COPYING.LESSER']:
            shutil.copy2(SKILL/'assets'/license_name,runtime/license_name)
        (package/'启动说明.txt').write_text(f'把本包全部文件放在 {game.name} 同目录，双击 {name}。\n保留 {support} 文件夹；移动整个游戏目录后仍可使用。\n自动模拟日文 CP932，不更改系统区域。原 EXE、存档、汉化和文本不修改。\n这是免手动转区启动器，不是原生 Unicode 二进制补丁。\n验证：仅完成构建；运行环境和游戏表现需另外测试。\n可执行启动器 --check 检查文件；日志位于配套目录 launcher-check.txt。\n卸载只删除本包新增的启动器及配套目录。\nLocale Emulator 2.5.0.1 官方组件：https://github.com/xupefei/Locale-Emulator/releases/tag/v2.5.0.1\n源码：https://github.com/xupefei/Locale-Emulator/tree/v2.5.0.1\n核心：https://github.com/xupefei/Locale-Emulator-Core\nLECommonLibrary.dll 从官方安装器资源提取；未运行安装器。\n许可证和自制启动器源码位于配套目录。\n',encoding='utf-8-sig')
        if sha(game)!=before: raise ValueError('Target changed during build')
        manifest={'target_name':game.name,'target_sha256':before,'launcher':name,'support_dir':support,'profile_guid':guid,'runtime_zip_sha256':ARCHIVE_SHA256,'locale':'ja-JP','runtime_verified':False,'game_verified':False,'files':{p.relative_to(package).as_posix():sha(p) for p in package.rglob('*') if p.is_file()}}
        (runtime/'build-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
        package.rename(out)
    print(json.dumps({'output':str(out),'target_unchanged':True,'runtime_verified':False},ensure_ascii=True))

if __name__=='__main__':
    main()
