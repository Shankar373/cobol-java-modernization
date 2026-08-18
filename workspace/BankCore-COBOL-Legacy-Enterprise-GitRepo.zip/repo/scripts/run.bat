@echo off
setlocal
if not exist bin\bankcore.exe (
  echo Run scripts\build.bat first.
  exit /b 1
)
if exist data\work\customer.dat del /q data\work\customer.dat
if exist data\work\account.dat del /q data\work\account.dat
if exist data\out\transaction-audit.dat del /q data\out\transaction-audit.dat
if exist data\out\transaction-exceptions.dat del /q data\out\transaction-exceptions.dat
if exist data\out\end-of-day-report.txt del /q data\out\end-of-day-report.txt
bin\bankcore.exe
echo.
echo ===== END-OF-DAY REPORT =====
type data\out\end-of-day-report.txt
echo.
echo ===== AUDIT =====
type data\out\transaction-audit.dat
echo.
echo ===== EXCEPTIONS =====
type data\out\transaction-exceptions.dat
