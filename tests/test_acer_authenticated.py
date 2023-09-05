# coding=utf-8
"""Logged-in Acer: requires ACFUNSDK_TEST_LOADING + cookie file (see conftest)."""

import pytest
from httpx import Client

from acfunsdk.page.acer import (
    BananaMall,
    MyAlbum,
    MyContribute,
    MyDanmaku,
    MyFansClub,
    MyFavourite,
    MyFollow,
)
from acfunsdk.page.message import MyMessage
from acfunsdk.page.moment import MyMoment


@pytest.mark.integration
@pytest.mark.requires_cookies
def test_logged_in_client_and_device_id(acer_logged_in):
    assert isinstance(acer_logged_in.client, Client)
    assert acer_logged_in.did.startswith("web_")
    assert 12 <= len(acer_logged_in.did) <= 32


@pytest.mark.integration
@pytest.mark.requires_cookies
def test_logged_in_tokens_and_flags(acer_logged_in):
    assert isinstance(acer_logged_in.uid, int)
    assert isinstance(acer_logged_in.username, str)
    assert "ssecurity" in acer_logged_in.tokens
    assert "api_st" in acer_logged_in.tokens
    assert "api_at" in acer_logged_in.tokens
    assert acer_logged_in.is_logined is True


@pytest.mark.integration
@pytest.mark.requires_cookies
def test_logged_in_submodules_types(acer_logged_in):
    assert isinstance(acer_logged_in.message, MyMessage)
    assert isinstance(acer_logged_in.moment, MyMoment)
    assert isinstance(acer_logged_in.follow, MyFollow)
    assert isinstance(acer_logged_in.favourite, MyFavourite)
    assert isinstance(acer_logged_in.danmaku, MyDanmaku)
    assert isinstance(acer_logged_in.contribute, MyContribute)
    assert isinstance(acer_logged_in.fansclub, MyFansClub)
    assert isinstance(acer_logged_in.album, MyAlbum)
    assert isinstance(acer_logged_in.bananamall, BananaMall)


@pytest.mark.integration
@pytest.mark.requires_cookies
@pytest.mark.writes_account_state
def test_signin_idempotent_or_success(acer_logged_in):
    assert acer_logged_in.signin() is True


@pytest.mark.integration
@pytest.mark.requires_cookies
def test_acoin_balance_shape(acer_logged_in):
    data = acer_logged_in.acoin()
    assert data is not None
    assert "aCoinAmount" in data
