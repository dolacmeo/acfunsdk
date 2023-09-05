# coding=utf-8
"""Visitor-mode Acer: live AcFun integration (no credentials)."""

import pytest
from httpx import Client

from tests.demo_urls import DEMO_GET_URLS


@pytest.mark.integration
def test_visitor_client_and_device_id(acer_visitor):
    assert isinstance(acer_visitor.client, Client)
    assert acer_visitor.did.startswith("web_")
    # 长度由服务端决定，曾常见 20，现为 18 等，只做宽松校验
    assert 12 <= len(acer_visitor.did) <= 32


@pytest.mark.integration
def test_visitor_tokens_and_login_flags(acer_visitor):
    assert "userId" in acer_visitor.tokens
    assert isinstance(acer_visitor.uid, int)
    assert acer_visitor.username is None
    assert "ssecurity" in acer_visitor.tokens
    assert "visitor_st" in acer_visitor.tokens
    assert acer_visitor.is_logined is False


@pytest.mark.integration
def test_visitor_logged_in_modules_uninitialized(acer_visitor):
    assert acer_visitor.message is None
    assert acer_visitor.moment is None
    assert acer_visitor.follow is None
    assert acer_visitor.favourite is None
    assert acer_visitor.danmaku is None
    assert acer_visitor.contribute is None
    assert acer_visitor.fansclub is None
    assert acer_visitor.album is None
    assert acer_visitor.bananamall is None


@pytest.mark.integration
@pytest.mark.parametrize("label,url", DEMO_GET_URLS, ids=[x[0] for x in DEMO_GET_URLS])
def test_visitor_get_public_demo_url(acer_visitor, label: str, url: str):
    """每条 URL 应与 examples/acer_demo.py 中对应 acer.get(...) 一致。"""
    obj = acer_visitor.get(url)
    assert obj is not None
    assert repr(obj)
