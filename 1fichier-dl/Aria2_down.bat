@ECHO OFF
if "%~1"=="" goto blank
for /F "tokens=*" %%A in (%~1) do python cli_aria2.py %%A
pause
exit

:blank
echo Usage: Aria2_down.bat [Link txt file]
echo (Link txt file one link per line)
set /p link=Input link:
python cli_aria2.py %link%
pause
exit
