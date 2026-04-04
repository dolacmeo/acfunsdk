# coding=utf-8
from __future__ import annotations

import os
from pathlib import Path

import pytest

from acfunsdk import Acer
from acfunsdk.exceptions import TingBuDong


@pytest.fixture
def acfun_loading_username() -> str | None:
    """Account label for Acer(loading=...); must match '<name>.cookies' filename."""
    return os.environ.get("ACFUNSDK_TEST_LOADING")


@pytest.fixture
def acfun_cookie_dir() -> Path:
    """Directory containing '<ACFUNSDK_TEST_LOADING>.cookies'. Default: tests/."""
    raw = os.environ.get("ACFUNSDK_TEST_COOKIE_DIR")
    if raw:
        return Path(raw).resolve()
    return Path(__file__).resolve().parent


@pytest.fixture
def acfun_authenticated_username(
    acfun_loading_username: str | None,
    acfun_cookie_dir: Path,
) -> str:
    """Resolve loading username and ensure cookie file exists (else skip)."""
    if not acfun_loading_username:
        pytest.skip(
            "Set ACFUNSDK_TEST_LOADING to the cookie basename "
            "(e.g. dolacmeo@qq.com for dolacmeo@qq.com.cookies). "
            "Optional: ACCFUNSDK_TEST_COOKIE_DIR points to the folder containing that file.",
        )
    cookie = acfun_cookie_dir / f"{acfun_loading_username}.cookies"
    if not cookie.is_file():
        pytest.skip(f"Cookie file not found: {cookie}")
    return acfun_loading_username


@pytest.fixture
def acer_visitor() -> Acer:
    """Live Acer in visitor mode (hits AcFun on construction)."""
    return Acer()


@pytest.fixture
def acer_logged_in(
    acfun_authenticated_username: str,
    acfun_cookie_dir: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> Acer:
    """Acer restored from cookies; cwd temporarily set so loading() finds the file."""
    monkeypatch.chdir(acfun_cookie_dir)
    try:
        return Acer(loading=acfun_authenticated_username)
    except (AssertionError, TingBuDong) as exc:
        pytest.skip(f"Acer(loading=…) failed (expired or invalid cookies?): {exc}")
