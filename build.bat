@echo off
set /p buildstuff=Alright then. Press enter if you're  sure you want to do this.
pyinstaller --onefile --add-data="sounds.dat;." fighter.pyw
pause