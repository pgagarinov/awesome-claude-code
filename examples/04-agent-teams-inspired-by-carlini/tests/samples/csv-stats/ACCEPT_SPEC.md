# Acceptance Criteria: CSV Stats

1. **load_csv works**: `from stats import load_csv; rows = load_csv("sample.csv")` returns a list of 10 dicts, each with keys `name`, `age`, `score`.
2. **Numeric conversion**: `rows[0]["age"]` is a numeric type (int or float), not a string.
3. **compute_stats works**: `from stats import compute_stats; s = compute_stats(rows, "score")` returns a dict with keys `min`, `max`, `mean`, `median`.
4. **compute_stats correct values**: For the `score` column: min=69, max=95, mean=82.9, median=84.0.
5. **filter_rows works**: `from stats import filter_rows; filtered = filter_rows(rows, "age", ">", 30)` returns rows where age > 30 (Charlie age=35, Eve age=31, Hank age=33, Jack age=40 — 4 rows).
6. **filter_rows equality**: `filter_rows(rows, "name", "==", "Alice")` returns exactly 1 row.
7. **CLI runs**: `python stats.py sample.csv --column score` exits with code 0 and output contains the word "mean" or "Mean".
8. **CLI with filter**: `python stats.py sample.csv --column score --filter "age>25"` exits with code 0.
9. **test file exists**: `test_stats.py` exists.
10. **tests pass**: `python -m pytest test_stats.py -v` exits with code 0 and reports at least 8 passing tests.
