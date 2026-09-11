========================================================
MENTOR COBOL -> JAVA DIFFERENTIAL VALIDATION
========================================================

Programs Tested: 6

Conversion:
6 SUCCESS
0 FAIL
0 BLOCKED

Compilation:
6 PASS
0 FAIL
0 BLOCKED

COBOL Runtime:
3 PASS
3 FAIL
0 BLOCKED

Java Runtime:
1 PASS
5 FAIL
0 BLOCKED

Business Equivalence:
1 PASS
0 WARNING
3 FAIL
2 UNPROVEN
0 BLOCKED

Unsupported Constructs: 0
Warnings: 3

False Business-Equivalence PASS: 0
Mutation Detection: 7/7 (100%)

========================================================
SUCCESSFUL DEMONSTRATION
========================================================

Program: SIMPLEBASELINE01

COBOL:
SIMPLEBASELINE01 START
ADD RESULT: 00075
COMPUTE RESULT: 01260
SIMPLEBASELINE01 END

JAVA:
SIMPLEBASELINE01 START
ADD RESULT: 00075
COMPUTE RESULT: 01260
SIMPLEBASELINE01 END

Comparison: MATCH
Business Equivalence: PASS

========================================================