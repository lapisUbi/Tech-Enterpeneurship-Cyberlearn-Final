@echo off
setlocal
set "DST=%LOCALAPPDATA%\CyberLearnCampusQuest"
if not exist "%DST%" mkdir "%DST%"
for %%F in (CyberLearn.html classroom.py bank_rules.json Start_Class_Windows.cmd READ_ME_EN.txt) do copy /Y "%~dp0%%F" "%DST%\%%F" >nul || goto fail
start "" "%DST%\CyberLearn.html"
echo Installed in %DST%. Open CyberLearn.html here to run it again.
pause
exit /b 0
:fail
echo Could not finish the local install. Open CyberLearn.html in the extracted folder instead.
pause
exit /b 1
