[Setup]
AppId={{F7D5E4A1-6B3C-4D2E-8A1F-9E8B7C6A5D4E}
AppName=bToDo Calendar
AppVersion=1.0 
AppPublisher=Britton Applications
DefaultDirName={autopf}\bToDo Calendar
DefaultGroupName=bToDo Calendar
AllowNoIcons=yes
OutputBaseFilename=bToDo_Setup
SetupIconFile=C:\BrittonCalendar\britton.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "C:\BrittonCalendar\dist\bToDo\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\bToDo Calendar"; Filename: "{app}\bToDo.exe"