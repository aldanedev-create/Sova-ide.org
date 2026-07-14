#ifndef AppVersion
  #define AppVersion "0.1.0"
#endif
#define PlatformRoot "..\.."
#define ReleaseRoot "..\..\release"
#define StagingRoot "..\..\release\staging\Sova"

[Setup]
AppId={{0AE8B221-12E8-4E43-9E3A-6A2CF3B41260}
AppName=Sova Programming Language
AppVersion={#AppVersion}
AppPublisher=Sova Language Project
AppPublisherURL=https://sova-lang.vercel.app/
AppSupportURL=https://sova-lang.vercel.app/install
AppUpdatesURL=https://sova-lang.vercel.app/releases
DefaultDirName={autopf}\Sova
DefaultGroupName=Sova
OutputDir={#ReleaseRoot}
OutputBaseFilename=SovaSetup-x64-{#AppVersion}
LicenseFile=licenses\LICENSE.txt
SetupIconFile=assets\sova.ico
WizardImageFile=assets\wizard-image.bmp
WizardSmallImageFile=assets\wizard-small.bmp
UninstallDisplayIcon={app}\sova.ico
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=admin
ChangesEnvironment=yes
ChangesAssociations=yes
VersionInfoVersion={#AppVersion}.0
VersionInfoCompany=Sova Language Project
VersionInfoDescription=Sova Programming Language Installer
VersionInfoProductName=Sova Programming Language

[Components]
Name: "runtime"; Description: "Sova Runtime"; Types: full compact custom; Flags: fixed
Name: "cli"; Description: "Sova CLI and shell"; Types: full compact custom; Flags: fixed
Name: "stdlib"; Description: "Sova standard-library source"; Types: full custom
Name: "examples"; Description: "Sova examples"; Types: full custom
Name: "docs"; Description: "Offline documentation"; Types: full custom

[Tasks]
Name: "addtopath"; Description: "Add Sova to the system PATH"; GroupDescription: "System integration:"; Flags: checkedonce
Name: "associate"; Description: "Associate .sova files with Sova"; GroupDescription: "System integration:"; Flags: checkedonce
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Shortcuts:"; Flags: unchecked
Name: "opendocs"; Description: "Open Sova documentation after setup"; GroupDescription: "After installation:"; Flags: unchecked
Name: "vscodeextension"; Description: "Install Sova support for Visual Studio Code"; GroupDescription: "Editor integration:"; Flags: checkedonce
Name: "vscodiumextension"; Description: "Install Sova support for VSCodium"; GroupDescription: "Editor integration:"; Flags: unchecked
Name: "cursorextension"; Description: "Install Sova support for Cursor"; GroupDescription: "Editor integration:"; Flags: unchecked
Name: "windsurfextension"; Description: "Install Sova support for Windsurf"; GroupDescription: "Editor integration:"; Flags: unchecked

[Dirs]
Name: "{app}\bin"

[Files]
Source: "{#StagingRoot}\bin\sova.exe"; DestDir: "{app}\bin"; Components: runtime cli; Flags: ignoreversion
Source: "{#StagingRoot}\bin\sova-shell.exe"; DestDir: "{app}\bin"; Components: cli; Flags: ignoreversion
Source: "{#StagingRoot}\bin\sovafmt.exe"; DestDir: "{app}\bin"; Components: cli; Flags: ignoreversion
Source: "{#StagingRoot}\bin\sovalint.exe"; DestDir: "{app}\bin"; Components: cli; Flags: ignoreversion
Source: "{#StagingRoot}\bin\sova-doc.exe"; DestDir: "{app}\bin"; Components: cli; Flags: ignoreversion
Source: "{#StagingRoot}\runtime\*"; DestDir: "{app}\runtime"; Components: runtime; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{#StagingRoot}\stdlib\*"; DestDir: "{app}\stdlib"; Components: stdlib; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{#StagingRoot}\examples\*"; DestDir: "{app}\examples"; Components: examples; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{#StagingRoot}\docs\*"; DestDir: "{app}\docs"; Components: docs; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{#StagingRoot}\LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#StagingRoot}\README.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "assets\sova.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#StagingRoot}\editor\vscode\sova\*"; DestDir: "{%USERPROFILE}\.vscode\extensions\sova.sova-language-0.1.0"; Flags: ignoreversion recursesubdirs createallsubdirs; Tasks: vscodeextension
Source: "{#StagingRoot}\editor\vscode\sova\*"; DestDir: "{%USERPROFILE}\.vscode-oss\extensions\sova.sova-language-0.1.0"; Flags: ignoreversion recursesubdirs createallsubdirs; Tasks: vscodiumextension
Source: "{#StagingRoot}\editor\vscode\sova\*"; DestDir: "{%USERPROFILE}\.cursor\extensions\sova.sova-language-0.1.0"; Flags: ignoreversion recursesubdirs createallsubdirs; Tasks: cursorextension
Source: "{#StagingRoot}\editor\vscode\sova\*"; DestDir: "{%USERPROFILE}\.windsurf\extensions\sova.sova-language-0.1.0"; Flags: ignoreversion recursesubdirs createallsubdirs; Tasks: windsurfextension

[Icons]
Name: "{group}\Sova Shell"; Filename: "{app}\bin\sova-shell.exe"; WorkingDir: "{app}\examples"; IconFilename: "{app}\sova.ico"
Name: "{group}\Sova Documentation"; Filename: "{app}\docs\language-overview.md"; IconFilename: "{app}\sova.ico"
Name: "{group}\Uninstall Sova"; Filename: "{uninstallexe}"; IconFilename: "{app}\sova.ico"
Name: "{commondesktop}\Sova Shell"; Filename: "{app}\bin\sova-shell.exe"; WorkingDir: "{app}\examples"; Tasks: desktopicon; IconFilename: "{app}\sova.ico"

[Registry]
Root: HKCR; Subkey: ".sova"; ValueType: string; ValueName: ""; ValueData: "Sova.SourceFile"; Tasks: associate; Flags: uninsdeletevalue
Root: HKCR; Subkey: "Sova.SourceFile"; ValueType: string; ValueName: ""; ValueData: "Sova Source File"; Tasks: associate; Flags: uninsdeletekey
Root: HKCR; Subkey: "Sova.SourceFile\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\sova.ico,0"; Tasks: associate
Root: HKCR; Subkey: "Sova.SourceFile\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\bin\sova.exe"" run ""%1"""; Tasks: associate

[Run]
Filename: "{app}\docs\language-overview.md"; Description: "Open Sova documentation"; Flags: postinstall shellexec skipifsilent unchecked; Tasks: opendocs
Filename: "{app}\bin\sova.exe"; Parameters: "version"; Description: "Verify Sova installation"; Flags: postinstall skipifsilent runhidden

[UninstallDelete]
Type: filesandordirs; Name: "{%USERPROFILE}\.vscode\extensions\sova.sova-language-0.1.0"
Type: filesandordirs; Name: "{%USERPROFILE}\.vscode-oss\extensions\sova.sova-language-0.1.0"
Type: filesandordirs; Name: "{%USERPROFILE}\.cursor\extensions\sova.sova-language-0.1.0"
Type: filesandordirs; Name: "{%USERPROFILE}\.windsurf\extensions\sova.sova-language-0.1.0"

[Code]
function PathContains(PathValue: String; Dir: String): Boolean;
begin
  Result := Pos(';' + Lowercase(Dir) + ';', ';' + Lowercase(PathValue) + ';') > 0;
end;

procedure AddToSystemPath(Dir: String);
var
  CurrentPath: String;
begin
  if not RegQueryStringValue(HKLM, 'SYSTEM\CurrentControlSet\Control\Session Manager\Environment', 'Path', CurrentPath) then
    CurrentPath := '';
  if PathContains(CurrentPath, Dir) then exit;
  if CurrentPath <> '' then CurrentPath := CurrentPath + ';';
  RegWriteExpandStringValue(HKLM, 'SYSTEM\CurrentControlSet\Control\Session Manager\Environment', 'Path', CurrentPath + Dir);
end;

procedure RemoveFromSystemPath(Dir: String);
var
  CurrentPath, Remaining, NewPath, Item, Comparable: String;
  Separator: Integer;
begin
  if not RegQueryStringValue(HKLM, 'SYSTEM\CurrentControlSet\Control\Session Manager\Environment', 'Path', CurrentPath) then exit;
  Remaining := CurrentPath + ';';
  NewPath := '';
  while Remaining <> '' do begin
    Separator := Pos(';', Remaining);
    if Separator = 0 then begin Item := Remaining; Remaining := ''; end
    else begin Item := Copy(Remaining, 1, Separator - 1); Delete(Remaining, 1, Separator); end;
    Item := Trim(Item);
    Comparable := Item;
    if (Length(Comparable) >= 2) and (Comparable[1] = '"') and (Comparable[Length(Comparable)] = '"') then
      Comparable := Copy(Comparable, 2, Length(Comparable) - 2);
    if (Item <> '') and (CompareText(Comparable, Dir) <> 0) then begin
      if NewPath <> '' then NewPath := NewPath + ';';
      NewPath := NewPath + Item;
    end;
  end;
  RegWriteExpandStringValue(HKLM, 'SYSTEM\CurrentControlSet\Control\Session Manager\Environment', 'Path', NewPath);
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if (CurStep = ssPostInstall) and WizardIsTaskSelected('addtopath') then AddToSystemPath(ExpandConstant('{app}\bin'));
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usUninstall then RemoveFromSystemPath(ExpandConstant('{app}\bin'));
end;
