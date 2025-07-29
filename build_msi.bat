@echo off
if not exist "gui\app.py" (
	echo ERROR: Source file gui\app.py not found.
	pause
	exit /b 1
)
pyinstaller --onefile --noconsole gui/app.py -n NetworkScanner
if "%ERRORLEVEL%"== "0" (
	ISCC.exe setup_inno.iss
) else if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
	"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" setup_inno.iss
) else (
	echo ISCC.exe not found. Please install Inno Setup 6 and add it to your PATH.
	exit /b 1
)
pause