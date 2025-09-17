@echo off
set /p packsounds=Press enter to get packing!
cd sounds
"C:\Users\parker\Documents\old_fighter_remake\packer.py" sounds.dat yes
move sounds.dat ..
pause