# BookFlow SQE Viva Rehearsal

This preparation sheet is separate from the formal evidence report.

1. Run one focused JUnit test and explain why rejection paths assert that no repository save occurs.
2. Change the borrow limit from 3 to 4. Predict which 2/3/4 boundary expectations, MCC setup and custom mutation checks will change.
3. Change the two OpenAPI constraints and regenerate the data. Identify the exact generated values that change.
4. Explain why 100% selected-service coverage can coexist with lower whole-project coverage.
5. Explain the five equivalent PIT mutants and why a surviving mutant does not always mean a missing test.
6. Demonstrate the MySQL rollback test, retry it successfully, and show that no duplicate loan is created.
7. Explain why the release decision remains HOLD even though browser tests and the SonarQube quality gate pass.

Each member should be ready to locate the supporting test, execute it, interpret the evidence and explain the limitation of the result.
