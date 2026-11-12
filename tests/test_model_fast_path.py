"""The compiled fast path must be indistinguishable from the general validator."""
from enum import Enum
from typing import Literal, Optional
from uuid import UUID

import pytest

from cheema import models
from cheema.errors import HTTPError
from cheema.models import Model, compile_model_validator, field, field_validator, type_validator


class Color(Enum):
    RED = "red"
    BLUE = "blue"


class Tile(Model):
    id: int = field(ge=0)
    name: str = field(min_len=1, max_len=10)
    ratio: float = 1.0
    visible: bool = True
    color: Color = Color.RED
    kind: Literal["a", "b"] = "a"
    ref: Optional[UUID] = None


class Dash(Model):
    title: str
    tags: list[str] = field(max_items=3)
    filters: dict[str, int]
    tiles: list[Tile]
    note: Optional[str] = None


GOOD = {
    "title": "t",
    "tags": ["x", "y"],
    "filters": {"a": 1},
    "tiles": [{"id": 1, "name": "n", "ratio": 2, "color": "blue", "kind": "b", "ref": "12345678-1234-5678-1234-567812345678"}],
}

BAD = [
    {**GOOD, "title": 5},
    {k: v for k, v in GOOD.items() if k != "title"},
    {**GOOD, "tags": ["a", "b", "c", "d"]},
    {**GOOD, "tags": "nope"},
    {**GOOD, "filters": {"a": "1"}},
    {**GOOD, "filters": {"a": True}},
    {**GOOD, "tiles": [{"id": -1, "name": "n"}]},
    {**GOOD, "tiles": [{"id": 1, "name": ""}]},
    {**GOOD, "tiles": [{"id": 1, "name": "x" * 11}]},
    {**GOOD, "tiles": [{"id": 1.5, "name": "n"}]},
    {**GOOD, "tiles": [{"id": 1, "name": "n", "color": "green"}]},
    {**GOOD, "tiles": [{"id": 1, "name": "n", "kind": "z"}]},
    {**GOOD, "tiles": [{"id": 1, "name": "n", "visible": 1}]},
    {**GOOD, "tiles": [{"id": 1, "name": "n", "ref": "not-a-uuid"}]},
    {**GOOD, "tiles": [{"id": 1}]},
    {**GOOD, "tiles": [3]},
    [1, 2],
    None,
]


def _run(validator, data):
    try:
        return "ok", validator(data)
    except HTTPError as exc:
        return "err", (exc.status, exc.message, exc.detail)


def _slow(monkeypatch):
    monkeypatch.setattr(models, "_fast_model", lambda cls: None)
    monkeypatch.setattr(models, "_FAST_MODELS", {})


def test_fast_path_is_active_for_plain_models():
    assert models._fast_model(Dash) is not None


@pytest.mark.parametrize("payload", [GOOD, *BAD])
def test_fast_and_slow_paths_agree(payload, monkeypatch):
    v = compile_model_validator(Dash)
    fast = _run(v, payload)
    _slow(monkeypatch)
    slow = _run(v, payload)
    assert fast == slow


def test_good_payload_values_and_attribute_access():
    out = compile_model_validator(Dash)(GOOD)
    tile = out["tiles"][0]
    assert tile.ratio == 2.0 and isinstance(tile.ratio, float)
    assert tile.color is Color.BLUE
    assert isinstance(tile.ref, UUID)
    assert out.note is None and tile.visible is True


def test_models_with_validators_keep_general_path_and_run_hooks_once():
    calls = []

    class Hooked(Model):
        n: int

        @field_validator("n")
        def bump(cls, v):
            calls.append(v)
            return v + 1

    assert models._fast_model(Hooked) is None
    assert compile_model_validator(Hooked)({"n": 1})["n"] == 2
    assert calls == [1]


def test_type_validator_registered_after_first_use_still_applies():
    class Money(int):
        pass

    class Order(Model):
        total: Money

    v = compile_model_validator(Order)
    assert v({"total": 5})["total"] == 5  # fast path warmed up

    @type_validator(Money)
    def _double(value):
        return value * 2

    try:
        assert v({"total": 5})["total"] == 10
    finally:
        models._TYPE_VALIDATORS.pop(Money, None)
        models._FAST_MODELS.clear()


def test_self_referential_model_falls_back_cleanly():
    class Node(Model):
        name: str
        children: list["Node"] = []

    v = compile_model_validator(Node)
    assert v({"name": "a"})["name"] == "a"
