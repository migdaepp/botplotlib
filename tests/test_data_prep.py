"""Tests for botplotlib.compiler.data_prep."""

from __future__ import annotations

import pytest

from botplotlib.compiler.data_prep import normalize_data


class TestDictInput:
    """Test dispatch path 1: dict input."""

    def test_dict_with_lists(self) -> None:
        data = {"x": [1, 2, 3], "y": [4, 5, 6]}
        result = normalize_data(data)
        assert result == {"x": [1, 2, 3], "y": [4, 5, 6]}

    def test_dict_with_tuples(self) -> None:
        data = {"x": (1, 2, 3), "y": (4, 5, 6)}
        result = normalize_data(data)
        assert result == {"x": [1, 2, 3], "y": [4, 5, 6]}

    def test_dict_with_scalar_values(self) -> None:
        data = {"x": 42}
        result = normalize_data(data)
        assert result == {"x": [42]}

    def test_dict_keys_converted_to_string(self) -> None:
        data = {0: [1, 2], 1: [3, 4]}
        result = normalize_data(data)
        assert "0" in result
        assert "1" in result


class TestListOfDicts:
    """Test dispatch path 2: list[dict] input."""

    def test_records_to_columnar(self) -> None:
        data = [{"x": 1, "y": 4}, {"x": 2, "y": 5}, {"x": 3, "y": 6}]
        result = normalize_data(data)
        assert result == {"x": [1, 2, 3], "y": [4, 5, 6]}

    def test_empty_list(self) -> None:
        assert normalize_data([]) == {}

    def test_missing_keys_filled_with_none(self) -> None:
        data = [{"x": 1, "y": 2}, {"x": 3}]
        result = normalize_data(data)
        assert result["x"] == [1, 3]
        assert result["y"] == [2, None]

    def test_list_of_non_dicts_raises(self) -> None:
        with pytest.raises(TypeError, match="list of dicts"):
            normalize_data([1, 2, 3])


class TestGenerator:
    """Test dispatch path 6: generator input."""

    def test_generator_of_dicts(self) -> None:
        def gen():
            yield {"x": 1, "y": 4}
            yield {"x": 2, "y": 5}

        result = normalize_data(gen())
        assert result == {"x": [1, 2], "y": [4, 5]}

    def test_empty_generator(self) -> None:
        def gen():
            return
            yield  # noqa: unreachable

        result = normalize_data(gen())
        assert result == {}

    def test_generator_of_non_dicts_raises(self) -> None:
        def gen():
            yield 1
            yield 2

        with pytest.raises(TypeError, match="Generator yielded"):
            normalize_data(gen())


class TestUnsupported:
    """Test dispatch path 7: unsupported types."""

    def test_string_raises(self) -> None:
        with pytest.raises(TypeError, match="Unsupported data type"):
            normalize_data("hello")

    def test_int_raises(self) -> None:
        with pytest.raises(TypeError, match="Unsupported data type"):
            normalize_data(42)

    def test_none_raises(self) -> None:
        with pytest.raises(TypeError, match="Unsupported data type"):
            normalize_data(None)
