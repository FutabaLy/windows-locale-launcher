using System;
using System.IO;
using System.Reflection;
using System.Resources;
using System.Collections;
class ExtractCommon {
 static int Main(string[] args) {
  var assembly=Assembly.LoadFrom(args[0]);
  using(var stream=assembly.GetManifestResourceStream("LEInstaller.Properties.Resources.resources"))
  using(var reader=new ResourceReader(stream)) {
   foreach(DictionaryEntry entry in reader) {
    if((string)entry.Key=="LECommonLibrary") {
     byte[] bytes=entry.Value as byte[];
     if(bytes==null || bytes.Length<64 || bytes[0]!=77 || bytes[1]!=90) throw new Exception("Invalid embedded DLL");
     using(var output=new FileStream(args[1],FileMode.CreateNew)) output.Write(bytes,0,bytes.Length);
     return 0;
    }
   }
  }
  throw new Exception("LECommonLibrary resource not found");
 }
}
