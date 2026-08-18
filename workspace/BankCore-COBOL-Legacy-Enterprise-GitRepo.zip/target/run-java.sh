#!/usr/bin/env bash
# Run the transpiled batch (Docker).
REPO=C:\Users\bandi\Desktop\SystemaOps\Cobol-to-java-test\workspace\BankCore-COBOL-Legacy-Enterprise-GitRepo.zip\repo
TGT=C:\Users\bandi\Desktop\SystemaOps\Cobol-to-java-test\workspace\BankCore-COBOL-Legacy-Enterprise-GitRepo.zip\target
docker run --rm -v "$REPO:/repo" -v "$TGT:/target" -w /repo opensourcecobol/opensourcecobol4j:2.0.0 bash -c "java -cp /target/generated:/target/libcobj.jar BCMAIN01"
