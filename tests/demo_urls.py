# coding=utf-8
"""
仅用于 pytest 访客集成测试的 URL 列表（parametrize），不是给最终用户看的示例代码。

用法说明与逐条示例请以 examples/acer_demo.py 为准。
"""

from typing import Final

# (param id, url) — 与 examples/acer_demo.py 中各条 get() 保持一致，改 URL 时请两边同步
DEMO_GET_URLS: Final[tuple[tuple[str, str], ...]] = (
    ("video", "https://www.acfun.cn/v/ac4741185"),
    ("article", "https://www.acfun.cn/a/ac37416587"),
    ("album", "https://www.acfun.cn/a/aa6001205"),
    ("bangumi", "https://www.acfun.cn/bangumi/aa5023295"),
    ("up", "https://www.acfun.cn/u/39088"),
    ("moment", "https://www.acfun.cn/moment/am2797962"),
    ("live", "https://live.acfun.cn/live/378269"),
    ("share", "https://m.acfun.cn/v/?ac=37086357"),
    ("doodle", "https://hd.acfun.cn/doodle/knNWmnco.html"),
)
