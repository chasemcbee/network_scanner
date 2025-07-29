@echo off
pyinstaller --onefile --noconsole gui/app.py -n NetworkScanner
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" setup_inno.iss
pause