# coding=utf-8
"""首页 AcPagelet / AcIndex：DOM 与 bigPipe 解析容错（单元 + 可选集成）。"""

from types import SimpleNamespace

import pytest

from acfunsdk.page.index import AcPagelet


class _AcFun:
    nav_data: dict = {}

    @staticmethod
    def AcImage(*_a, **_kw):
        return None

    @staticmethod
    def AcVideo(*_a, **_kw):
        return None


@pytest.fixture
def fake_acer():
    return SimpleNamespace(acfun=_AcFun(), get=lambda url, title=None: None)


def test_pagelet_banner_bad_markup_returns_none(fake_acer):
    raw = {
        "id": "pagelet_banner",
        "html": "<div class='wrong'></div>",
        "styles": [],
    }
    p = AcPagelet(fake_acer, raw)
    assert p.to_dict(obj=False) is None


def test_pagelet_top_area_empty_scripts_still_returns_dict(fake_acer):
    raw = {"id": "pagelet_top_area", "html": "<div></div>", "scripts": []}
    p = AcPagelet(fake_acer, raw)
    out = p.to_dict(obj=False)
    assert isinstance(out, dict)
    assert out.get("slider") == []
    assert out.get("items") == []


@pytest.mark.integration
def test_acindex_get_pagelets_no_crash(acer_visitor):
    idx = acer_visitor.acfun.AcIndex()
    for area in ("banner", "header", "douga", "navigation", "footer"):
        out = idx.get(area, obj=False)
        assert out is None or isinstance(out, (dict, list))


@pytest.mark.integration
@pytest.mark.requires_cookies
def test_acindex_get_when_logged_in(acer_logged_in):
    idx = acer_logged_in.acfun.AcIndex()
    out = idx.get("banner", obj=False)
    assert out is None or isinstance(out, dict)
