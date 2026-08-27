
from Orange.data import ContinuousVariable, StringVariable

from cta_orange.helpers.orange_datatable import create_orange_datatable


def test_create_orange_datatable_infers_types():
    """Check the correctness of types, length and creation of the Orange datatable"""
    rows=[{"a":1, "b":"str1", "c":True},{"a":2, "b":"str2", "c":False}]
    table=create_orange_datatable(rows, ["a","b","c"])
    assert table is not None
    assert len(table) == 2

    a, b, c = table.domain.metas
    assert isinstance(a, ContinuousVariable)
    assert isinstance(b, StringVariable)
    assert isinstance(c, StringVariable)

def test_create_orange_datatable_preserves_numeric_values():
    """Check if the numeric values are interpreted as such with the conversion to datatable and not as strings"""
    rows = [{"a":1}, {"a":2}]
    table=create_orange_datatable(rows, ["a"])
    assert table.metas[0][0] == 1.0
    assert table.metas[1][0] == 2.0

def test_create_orange_datatable_empty_returns_none():
    """Check if the return table is none if no rows given"""
    assert create_orange_datatable([],["a"]) is None
