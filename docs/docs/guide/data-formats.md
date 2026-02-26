# Data Formats

botplotlib accepts basically anything that looks like data. Pass whatever your pipeline produces — the library handles conversion automatically through `normalize_data()`.

## Supported formats

### 1. Dict of columns (recommended)

The most direct format. Keys are column names, values are lists of equal length.

```python
import botplotlib as bpl

data = {
    "x": [1, 2, 3, 4, 5],
    "y": [10, 20, 15, 25, 30],
}
fig = bpl.scatter(data, x="x", y="y")
```

### 2. List of dicts (row-oriented records)

Common when data comes from JSON APIs or database queries.

```python
records = [
    {"language": "Python", "popularity": 30},
    {"language": "JavaScript", "popularity": 25},
    {"language": "TypeScript", "popularity": 18},
    {"language": "Rust", "popularity": 10},
]
fig = bpl.bar(records, x="language", y="popularity")
```

### 3. Polars DataFrame

```python
import polars as pl

df = pl.DataFrame({
    "x": [1, 2, 3, 4, 5],
    "y": [2, 4, 6, 8, 10],
})
fig = bpl.line(df, x="x", y="y")
```

### 4. Pandas DataFrame

```python
import pandas as pd

df = pd.DataFrame({
    "x": [1, 2, 3, 4, 5],
    "y": [2, 4, 6, 8, 10],
})
fig = bpl.line(df, x="x", y="y")
```

### 5. Arrow Table / RecordBatch

```python
import pyarrow as pa

table = pa.table({
    "x": [1, 2, 3, 4, 5],
    "y": [2, 4, 6, 8, 10],
})
fig = bpl.line(table, x="x", y="y")
```

### 6. Generator / iterator

Generators are materialized to a list of dicts, then transposed to columnar format.

```python
def data_gen():
    for i in range(10):
        yield {"x": i, "y": i ** 2}

fig = bpl.scatter(data_gen(), x="x", y="y")
```

## Dispatch order

`normalize_data()` checks formats in this exact order:

1. **dict** — checks `__getitem__` returns list-like values
2. **list[dict]** — transposes row-oriented records to columnar dict
3. **Polars DataFrame** — detects via `hasattr(data, "get_column")`
4. **Pandas DataFrame** — detects via `hasattr(data, "to_dict")` and `hasattr(data, "dtypes")`
5. **Arrow Table/RecordBatch** — detects via `hasattr(data, "column_names")` and `hasattr(data, "column")`
6. **Generator/iterator** — materializes to list of dicts, then applies step 2
7. **Raises `TypeError`** — lists supported formats in the error message

!!! tip
    No format conversion code is needed in your pipeline. Just pass the data through and botplotlib handles it. This is particularly valuable for LLM-generated code — the model doesn't need to know or reason about data format conversions.

## Column access

Once normalized, data is a `dict[str, list]`. Column names are passed as strings to `x`, `y`, and `color` parameters. If a column doesn't exist, the compiler raises a clear `ValueError` naming the missing column.
