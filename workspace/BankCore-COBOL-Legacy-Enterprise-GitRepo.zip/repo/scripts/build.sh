#!/usr/bin/env bash
set -e
mkdir -p bin
cobc -x -free -I copybooks -o bin/bankcore src/BCMAIN01.cob src/BCLOAD01.cob src/BCPROC01.cob src/BCREPT01.cob
echo "Build successful: bin/bankcore"
