@echo off
pyuic5 "%~nx1" -o "%~n1.py"
pause
exit /b