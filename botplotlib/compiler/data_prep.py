"""Data normalization for botplotlib.

Follows the stated column-access protocol documented in AGENTS.md:

1. dict — check __getitem__ returns list-like values → use directly
2. list[dict] — transpose row-oriented records to columnar dict
3. Polars DataFrame — hasattr(data, "get_column")
4. Pandas DataFrame — hasattr(data, "to_dict") and hasattr(data, "dtypes")
5. Arrow RecordBatch/Table — hasattr(data, "column_names") and hasattr(data, "column")
6. Generator/iterator — materialize to list-of-dicts, then apply step 2
7. Raise TypeError with supported types listed
"""

from __future__ import annotations

import types
from typing import Any


def _is_list_like(obj: Any) -> bool:
    """Check if an object is list-like (list, tuple, or has __len__ and __getitem__)."""
    if isinstance(obj, (list, tuple)):
        return True
    return hasattr(obj, "__len__") and hasattr(obj, "__getitem__")


def _transpose_records(records: list[dict]) -> dict[str, list]:
    """Transpose a list of row dicts to a columnar dict."""
    if not records:
        return {}
    columns: dict[str, list] = {}
    # Use all keys from all records for robustness
    all_keys: list[str] = []
    seen: set[str] = set()
    for record in records:
        for key in record:
            if key not in seen:
                all_keys.append(key)
                seen.add(key)
    for key in all_keys:
        columns[key] = [record.get(key) for record in records]
    return columns


def normalize_data(data: Any) -> dict[str, list]:
    """Normalize input data to a columnar dict.

    Follows the dispatch order documented in AGENTS.md.

    Parameters
    ----------
    data:
        Input data in any supported format.

    Returns
    -------
    dict[str, list]
        Columnar data with string keys and list values.

    Raises
    ------
    TypeError
        If the data format is not recognized.
    """
    # 1. dict with list-like values
    if isinstance(data, dict):
        result: dict[str, list] = {}
        for key, val in data.items():
            if _is_list_like(val):
                result[str(key)] = list(val)
            else:
                result[str(key)] = [val]
        return result

    # 2. list[dict] — row-oriented records
    if isinstance(data, list):
        if len(data) == 0:
            return {}
        if isinstance(data[0], dict):
            return _transpose_records(data)
        raise TypeError(
            f"Expected list of dicts, got list of {type(data[0]).__name__}. "
            "Supported formats: dict, list[dict], Polars DataFrame, "
            "Pandas DataFrame, Arrow Table/RecordBatch, generator."
        )

    # 3. Polars DataFrame
    if hasattr(data, "get_column") and hasattr(data, "columns"):
        return {
            col: data.get_column(col).to_list() for col in data.columns
        }

    # 4. Pandas DataFrame
    if hasattr(data, "to_dict") and hasattr(data, "dtypes"):
        return data.to_dict(orient="list")

    # 5. Arrow RecordBatch/Table
    if hasattr(data, "column_names") and hasattr(data, "column"):
        return {
            name: data.column(name).to_pylist() for name in data.column_names
        }

    # 6. Generator/iterator — materialize then transpose
    if isinstance(data, (types.GeneratorType,)) or (
        hasattr(data, "__iter__") and hasattr(data, "__next__")
    ):
        records = list(data)
        if not records:
            return {}
        if isinstance(records[0], dict):
            return _transpose_records(records)
        raise TypeError(
            f"Generator yielded {type(records[0]).__name__}, expected dicts. "
            "Supported formats: dict, list[dict], Polars DataFrame, "
            "Pandas DataFrame, Arrow Table/RecordBatch, generator of dicts."
        )

    # 7. Raise TypeError
    raise TypeError(
        f"Unsupported data type: {type(data).__name__}. "
        "Supported formats: dict, list[dict], Polars DataFrame, "
        "Pandas DataFrame, Arrow Table/RecordBatch, generator of dicts."
    )
