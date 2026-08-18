@echo off
REM Run the transpiled batch (Docker).
set REPO=C:\Users\bandi\Desktop\SystemaOps\Cobol-to-java-test\legacy
set TGT=C:\Users\bandi\Desktop\SystemaOps\Cobol-to-java-test\target
docker run --rm -v "%REPO%:/repo" -v "%TGT%:/target" -w /repo opensourcecobol/opensourcecobol4j:2.0.0 bash -c "java -cp /target/generated:/target/libcobj.jar CCMAIN01"
