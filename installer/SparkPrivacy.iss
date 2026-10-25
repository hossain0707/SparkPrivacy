#define AppName "SparkPrivacy"
#define AppVersion "0.1.0"
#define AppPublisher "Md Najmul Hossain"
[Setup]
AppId={{D6B41F5A-8AB5-4DB2-8C26-8C408324E291}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={localappdata}\Programs\SparkPrivacy
DefaultGroupName=SparkPrivacy
OutputDir=..\dist\release
OutputBaseFilename=SparkPrivacy-Setup-Windows-x64
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest
UninstallDisplayIcon={app}\SparkPrivacy.exe
SetupIconFile=..\assets\sparkprivacy-icon.ico
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
DisableProgramGroupPage=yes

[Files]
Source: "..\dist\SparkPrivacy\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion

[Icons]
Name: "{autoprograms}\SparkPrivacy"; Filename: "{app}\SparkPrivacy.exe"
Name: "{autodesktop}\SparkPrivacy"; Filename: "{app}\SparkPrivacy.exe"; Tasks: desktopicon

[Tasks]
Name: desktopicon; Description: "Create a desktop shortcut"; GroupDescription: "Additional icons:"

[Run]
Filename: "{app}\SparkPrivacy.exe"; Description: "Launch SparkPrivacy"; Flags: nowait postinstall skipifsilent
