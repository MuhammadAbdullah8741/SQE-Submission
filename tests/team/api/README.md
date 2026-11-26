# API test-data generation

Owner: M Umar (24i-3132)

The selected circulation endpoints are Spring MVC form/query operations. The
OpenAPI document models their inputs and observed HTTP contracts; it does not
mislabel them as a JSON REST API.

## Reproduce

From the repository root:

```powershell
python tests/team/api/generate.py
python tests/team/api/check_generation.py
node tests/team/api/run.cjs
```

The generator emits equivalence partitions and three-point boundary values for
every declared input. Only one input varies in each generated case so a failure
can be attributed to one partition or boundary. The executable runner resets
synthetic data between cases and reads back transactions and stock.

## Specification-change demonstration

The viva change demonstration modifies two constraints and regenerates data:

- `memberId.maxLength`: 25 to 20, changing lengths 24/25/26 to 19/20/21.
- `txnId.minimum`: 1 to 2, changing values 0/1/2 to 1/2/3.

`check_generation.py` verifies unique case IDs, required EP classes,
one-field-at-a-time variation, all three boundary neighbours and both expected
constraint deltas. The expected baseline and changed outputs each contain 52
cases.
