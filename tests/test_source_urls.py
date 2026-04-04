# coding=utf-8
"""
对 acfunsdk.source.AcSource 中声明的 HTTP(S) 与 WSS 地址做可达性探测。

- 使用与 SDK 相同的 AcSource.header；优先 HEAD，405/501 时改用 GET。
- routes 中与 tests/demo_urls.py 同名的 key 使用 DEMO 里的完整 URL（避免模板路径触发 502）。
- 个别上传接口在无正文时返回 500、部分 CDN 对简单探测稳定返回 502：见模块内
  _HTTP_PROBE_ALLOW_500 / _HTTP_PROBE_502_XFAIL；后者在 502 时记为 xfail，不导致套件失败。

标记：integration、source_urls（可在 pytest 中按标记筛选）。

环境变量：
- ACFUNSDK_SKIP_SOURCE_URLS=1：跳过本文件全部用例（无网络 CI）。
- ACFUNSDK_SOURCE_URL_TIMEOUT：单次请求超时秒数，默认 20。
"""

from __future__ import annotations

import os
import socket
import ssl
import time
from typing import Iterator
from urllib.parse import urlparse

import httpx
import pytest

from acfunsdk.source import AcSource

from tests.demo_urls import DEMO_GET_URLS

# routes 中若干 key 为「路径模板」（缺稿件/用户 ID 时站点可能返回 502），与 demo_urls 共用可访问的完整示例 URL。
_ROUTE_PROBE_BY_KEY: dict[str, str] = dict(DEMO_GET_URLS)

# HEAD/GET 探测上传类接口时，服务端常返回 500；视为「主机可达、路径存在」即可。
_HTTP_PROBE_ALLOW_500: frozenset[tuple[str, str]] = frozenset({("apis", "im_image_upload")})

# 部分快手系 CDN 对简单探测返回稳定 502，与业务侧可用性未必一致；遇 502 时记为 xfail 而非硬失败。
_HTTP_PROBE_502_XFAIL: frozenset[tuple[str, str]] = frozenset(
    {
        ("apis", "doodle_comment"),
        ("app_apis", "safetyid"),
        ("domains", "app_cdn"),
    }
)


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    if os.environ.get("ACFUNSDK_SKIP_SOURCE_URLS", "").strip().lower() not in (
        "1",
        "true",
        "yes",
    ):
        return
    skip = pytest.mark.skip(reason="ACFUNSDK_SKIP_SOURCE_URLS is set")
    for item in items:
        if "test_source_urls.py::" in item.nodeid:
            item.add_marker(skip)


def _iter_http_url_entries() -> Iterator[tuple[str, str, str]]:
    """Yield (section, key, url) for each HTTP(S) URL on AcSource."""
    s = AcSource
    for key, url in s.routes.items():
        yield ("routes", key, _ROUTE_PROBE_BY_KEY.get(key, url))
    for key, url in s.apis.items():
        yield ("apis", key, url)
    for key, url in s.app_apis.items():
        yield ("app_apis", key, url)
    for key, host in s.domains.items():
        yield ("domains", key, f"{s.scheme}://{host}/")
    yield ("static", "Weixin_qrcode_img", s.Weixin_qrcode_img)
    yield ("static", "ico", s.ico)
    yield ("static", "logo", s.logo)
    yield ("static", "login_bg", s.login_bg)
    for i, url in enumerate(s.danmaku_bg):
        yield ("static", f"danmaku_bg[{i}]", url)


HTTP_URL_ENTRIES: tuple[tuple[str, str, str], ...] = tuple(_iter_http_url_entries())
HTTP_URL_IDS: list[str] = [f"{sec}:{key}" for sec, key, _ in HTTP_URL_ENTRIES]

WS_URLS: tuple[str, ...] = tuple(AcSource.websocket_links)
WS_URL_IDS: list[str] = [urlparse(u).hostname or u for u in WS_URLS]


def _probe_http(client: httpx.Client, url: str, timeout: float) -> httpx.Response:
    """Prefer HEAD; fall back to GET when the server rejects HEAD."""
    try:
        head_resp = client.head(url, timeout=timeout)
    except httpx.HTTPError:
        return client.get(url, timeout=timeout)
    if head_resp.status_code in (405, 501):
        return client.get(url, timeout=timeout)
    return head_resp


def _probe_http_with_retry(client: httpx.Client, url: str, timeout: float) -> httpx.Response:
    """对偶发网关错误重试一次，减少误报。"""
    last = _probe_http(client, url, timeout=timeout)
    if last.status_code in (502, 503, 504):
        time.sleep(1.5)
        last = _probe_http(client, url, timeout=timeout)
    return last


def _assert_http_reachable(resp: httpx.Response, section: str, key: str, url: str) -> None:
    if (section, key) in _HTTP_PROBE_ALLOW_500 and resp.status_code == 500:
        return
    if resp.status_code == 502 and (section, key) in _HTTP_PROBE_502_XFAIL:
        pytest.xfail(
            "该地址在简单 HEAD/GET 探测下常返回 502（CDN/边缘策略）；"
            "仍保留在 AcSource 供客户端按协议调用。"
        )
    # 5xx 视为服务端或网关异常；4xx 仍说明主机与路径可达（鉴权/方法/参数不符等）
    assert resp.status_code < 500, (
        f"[{section}:{key}] {url} -> HTTP {resp.status_code}"
    )


@pytest.fixture(scope="module")
def source_url_timeout() -> float:
    return float(os.environ.get("ACFUNSDK_SOURCE_URL_TIMEOUT", "20"))


@pytest.fixture(scope="module")
def source_url_client() -> Iterator[httpx.Client]:
    with httpx.Client(headers=AcSource.header, follow_redirects=True) as client:
        yield client


@pytest.mark.integration
@pytest.mark.source_urls
@pytest.mark.parametrize(
    "section,key,url",
    HTTP_URL_ENTRIES,
    ids=HTTP_URL_IDS,
)
def test_ac_source_http_url_reachable(
    source_url_client: httpx.Client,
    source_url_timeout: float,
    section: str,
    key: str,
    url: str,
) -> None:
    resp = _probe_http_with_retry(
        source_url_client, url, timeout=source_url_timeout
    )
    _assert_http_reachable(resp, section, key, url)


@pytest.mark.integration
@pytest.mark.source_urls
@pytest.mark.parametrize("url", WS_URLS, ids=WS_URL_IDS)
def test_ac_source_websocket_tls_handshake(
    source_url_timeout: float,
    url: str,
) -> None:
    parsed = urlparse(url)
    host = parsed.hostname
    assert host, f"invalid websocket url: {url!r}"
    port = parsed.port or 443
    ctx = ssl.create_default_context()
    with socket.create_connection((host, port), timeout=source_url_timeout) as raw:
        with ctx.wrap_socket(raw, server_hostname=host):
            pass
