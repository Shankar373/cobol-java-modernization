@echo off
setlocal
if not exist bin mkdir bin
cobc -x -free -I copybooks -o bin\bankcore.exe src\BCMAIN01.cob src\BCLOAD01.cob src\BCPROC01.cob src\BCREPT01.cob
if errorlevel 1 (
  echo Build failed.
  exit /b 1
)
echo Build successful: bin\bankcore.exe
