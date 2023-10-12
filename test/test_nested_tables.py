from nested_tables import *
import pytest

def test_get_in():
    test1 = {"a": {"b": {"c": [1, 2, 3]}}}
    ks1 = ["a", "b", "c"]

    test2 = {"a": [0, {"b": [1, 2, 3]}]}
    ks2 = ["a", "d"]

    assert get_in(test1, ks1) == [1, 2, 3]
    assert get_in(test1, ks1, update=lambda x: x * 2) == [1, 2, 3, 1, 2, 3]
    assert get_in(test2, ks2) == None
    assert get_in(test2, ["a", 0, "b"]) == None
    assert get_in(test2, ["a", 1, "b"]) != None


def test_update_in():
    test = {"a": {"b": {"c": [1, 2, 3]}}}
    out = {"a": {"b": {"c": [1, 2, 3, 1, 2, 3]}}}
    out1 = {"a": {"z": {"c": {}}, "b": {"c": [1, 2, 3, 1, 2, 3]}}}

    assert update_in(test, ["a", "b", "c"], lambda x: x + [1, 2, 3]) == out
    assert update_in(test, ["a", "z", "c"], lambda x: x + [1, 2, 3], force=True) == out1


def test_pop_in():
    test = {"a": {"b": {"c": [1, 2, 3]}}}

    assert pop_in(test, ["a", "b"]) == (True, {"c": [1, 2, 3]})
    assert pop_in(test, ["a", "z"]) == (False, 1)


def test_grep():
    test = {"a": 1, "b": 2, "c": 10}
    test1 = [1, 2, 10]

    assert grep(lambda _, x: x % 2 == 0, test) == {"b": 2, "c": 10}
    assert grep(lambda x: x % 2 == 0, test1) == (2, 10)


def test_extend_in():
    test = {"a": [[1]], "b": 2, "c": 10}
    out = {"a": [[1, 2, 3, -1, -2], 2, 3, -1, -2], "b": 2, "c": 10}
    ks = ["a", 0]

    assert extend_in(test, ks, 2, 3, [-1, -2]) == [[1], 2, 3, -1, -2]
    assert extend_in(test, ["a", 0, 0], 2, 3, [-1, -2]) == [1, 2, 3, -1, -2]
    assert test == out


def test_append_in():
    test = {"a": [[1]], "b": 2, "c": 10}
    out = {"a": [[1, 2, 3], 2, 3], "b": 2, "c": 10}
    ks = ["a", 0]

    assert append_in(test, ks, 2, 3) == [[1], 2, 3]
    assert append_in(test, ["a", 0, 0], 2, 3) == [1, 2, 3]
    assert test == out


