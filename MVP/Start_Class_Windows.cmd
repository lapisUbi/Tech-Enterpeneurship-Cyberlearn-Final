@echo off
cd /d "%~dp0"
echo CyberLearn: trusted classroom network only. Keep the PRIVATE reviewer link on this computer.
where py >nul 2>nul
if errorlevel 1 (python classroom.py --lan) else (py -3 classroom.py --lan)
pause
