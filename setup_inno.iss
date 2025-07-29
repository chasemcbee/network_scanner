[Setup]
AppName=Network Scanner
AppVersion=1.0
DefaultDirName={pf}\NetworkScanner
DefaultGroupName=Network Scanner
OutputDir=Output
OutputBaseFilename=NetworkScannerInstaller
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\NetworkScanner.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Network Scanner"; Filename: "{app}\NetworkScanner.exe"
Name: "{commondesktop}\Network Scanner"; Filename: "{app}\NetworkScanner.exe"
