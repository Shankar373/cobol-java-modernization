#!/usr/bin/env bash
set -e
rm -f data/work/customer.dat data/work/account.dat
rm -f data/out/transaction-audit.dat data/out/transaction-exceptions.dat data/out/end-of-day-report.txt
./bin/bankcore
echo
echo "===== END-OF-DAY REPORT ====="
cat data/out/end-of-day-report.txt
echo
echo "===== AUDIT ====="
cat data/out/transaction-audit.dat
echo
echo "===== EXCEPTIONS ====="
cat data/out/transaction-exceptions.dat
