# acfunsdk - **UNOFFICEICAL**

<br />

<p align="center">
<a href="https://github.com/dolaCmeo/acfunsdk">
<img height="100" src="https://s3.dualstack.us-east-2.amazonaws.com/pythondotorg-assets/media/files/python-logo-only.svg" alt="">
<img height="100" src="https://ali-imgs.acfun.cn/kos/nlav10360/static/common/widget/header/img/acfunlogo.11a9841251f31e1a3316.svg" alt="">
</a>
</p>

<br />

acfunsdk是 **非官方的 [AcFun弹幕视频网][acfun.cn]** Python库。

> 声明：`acfunsdk`是python的学习工具，并未破解任何acfun相关内容。代码完全公开，仅用于交流学习。
> 如涉及版权等相关问题，请遵守acfun相关协议及法律法规。如有bug或其他疑问，欢迎发布[issues][Issue]。

- - -

**Python** : `Python>=3.10`， 本体请自行[下载安装][python]。

### [从PyPI安装](https://pypi.org/project/acfunsdk/)

```shell
python -m pip install acfunsdk
```

### 从源码开发（[uv](https://docs.astral.sh/uv/)）

```shell
uv sync --all-groups
uv run pytest
uv build
```

根目录 **`.python-version`** 固定为 **3.10**，`uv` 会按此创建/同步 `.venv`（可用 `uv python install 3.10` 安装解释器）。

**测试**（依赖外网；访客用例中的 URL 与 `examples/acer_demo.py` 对齐，列表仅在 `tests/demo_urls.py` 供 parametrize 使用）：

```shell
# 仅访客 / 公开 URL（适合 CI）
uv run pytest -m "not requires_cookies"
# 全量（需已配置登录 Cookie，见下）
uv run pytest
```

登录相关用例需环境变量 **`ACFUNSDK_TEST_LOADING`**（与 `Acer(loading=...)` 一致，且对应文件名 `<该字符串>.cookies`）。默认在 **`tests/`** 目录下查找 Cookie，可通过 **`ACFUNSDK_TEST_COOKIE_DIR`** 指定目录。

**示例脚本**（仓库根目录执行）：

```shell
python examples/acer_demo.py
```

> **相关组件**
> + [x] [`acfunsdk-ws`](https://github.com/dolaCmeo/acfunsdk-ws) 为`acfunsdk`提供websocket支持
> + [x] [`acsaver`](https://github.com/dolaCmeo/acsaver) 为`acfunsdk`提供内容保存下载功能
> + [ ] [`acfunsdk-cli`](https://github.com/dolaCmeo/acfunsdk-cli) 为`acfunsdk`提供命令行支持，TUI
- - -

## 使用方法


### 实例化获取对象
```python
from acfunsdk import Acer
# 实例化一个Acer
acer = Acer()
# 登录用户(成功登录后会自动保存 '<用户名>.cookies')
# 请注意保存，防止被盗
acer.login(username='you@email.com', password='balalabalala')
# 读取用户(读取成功登录后保存的 '<用户名>.cookies')
acer.loading(username='13800138000')
# 每日签到，领香蕉🍌
acer.signin()
# 通过链接直接获取内容对象
# 目前支持 9种内容类型：
# 视  频: https://www.acfun.cn/v/ac4741185
demo_video = acer.get("https://www.acfun.cn/v/ac4741185")
print(demo_video)
# 文  章: https://www.acfun.cn/a/ac37416587
demo_article = acer.get("https://www.acfun.cn/a/ac37416587")
print(demo_article)
# 合  集: https://www.acfun.cn/a/aa6001205
demo_album = acer.get("https://www.acfun.cn/a/aa6001205")
print(demo_album)
# 番  剧: https://www.acfun.cn/bangumi/aa5023295
demo_bangumi = acer.get("https://www.acfun.cn/bangumi/aa5023295")
print(demo_bangumi)
# 个人页: https://www.acfun.cn/u/39088
demo_up = acer.get("https://www.acfun.cn/u/39088")
print(demo_up)
# 动  态: https://www.acfun.cn/moment/am2797962
demo_moment = acer.get("https://www.acfun.cn/moment/am2797962")
print(demo_moment)
# 直  播: https://live.acfun.cn/live/378269
demo_live = acer.get("https://live.acfun.cn/live/378269")
print(demo_live)
# 分  享: https://m.acfun.cn/v/?ac=37086357
demo_share = acer.get("https://m.acfun.cn/v/?ac=37086357")
print(demo_share)
# 涂鸦(单页): https://hd.acfun.cn/doodle/knNWmnco.html
demo_doodle = acer.get("https://hd.acfun.cn/doodle/knNWmnco.html")
print(demo_doodle)
```

- - -


<details>
<summary>依赖库</summary>

**依赖: 以 `pyproject.toml` 为准**（`requirements.txt` 为 pip 兼容的简要列表）

+ [`httpx`](https://pypi.org/project/httpx/)`>=0.27`
+ [`lxml`](https://pypi.org/project/lxml/)`>=5.3`
+ [`beautifulsoup4`](https://pypi.org/project/beautifulsoup4/)`>=4.12`

</details>

- - - 
## 参考 & 鸣谢

+ [AcFun 助手](https://github.com/niuchaobo/acfun-helper) 是一个适用于 AcFun（ acfun.cn ） 的浏览器插件。
+ [AcFunDanmaku](https://github.com/wpscott/AcFunDanmaku) 是用C# 和 .Net 6编写的AcFun直播弹幕工具。
+ [实现自己的AcFun直播弹幕姬](https://www.acfun.cn/a/ac16695813) [@財布士醬](https://www.acfun.cn/u/311509)
+ QQ频道“AcFun开源⑨课”
+ 使用 [uv](https://docs.astral.sh/uv/) 管理依赖与构建

> Special Thanks:
> <p align="center"><strong>JetBrains Licenses for Open Source Development - Community Support</strong></p>
> <p align="center"><a href="https://jb.gg/OpenSourceSupport" target="_blank">
> <img height="100" src="https://resources.jetbrains.com/storage/products/company/brand/logos/jb_beam.svg" alt=""><img height="100" src="https://resources.jetbrains.com/storage/products/company/brand/logos/PyCharm.svg" alt="">
> </a></p>

- - - 

## About Me

[![ac彩娘-阿部高和](https://tx-free-imgs2.acfun.cn/kimg/bs2/zt-image-host/ChQwODliOGVhYzRjMTBmOGM0ZWY1ZRCIzNcv.gif)][dolacfun]
[♂ 整点大香蕉🍌][acfunsdk_page]
<img alt="AcFunCard" align="right" src="https://discovery.sunness.dev/39088">

- - - 

[dolacfun]: https://www.acfun.cn/u/39088
[acfunsdk_page]: https://www.acfun.cn/a/ac37416587

[acfun.cn]: https://www.acfun.cn/
[Issue]: https://github.com/dolaCmeo/acfunsdk/issues
[python]: https://www.python.org/downloads/
[venv]: https://docs.python.org/zh-cn/3.10/library/venv.html

[acer]: https://github.com/dolaCmeo/acfunsdk/blob/main/examples/acer_demo.py
[index]: https://github.com/dolaCmeo/acfunsdk/blob/main/examples/index_reader.py
[channel]: https://github.com/dolaCmeo/acfunsdk/blob/main/examples/channel_reader.py
[search]: https://github.com/dolaCmeo/acfunsdk/blob/main/examples/seach_reader.py

[bangumi]: https://github.com/dolaCmeo/acfunsdk/blob/main/examples/bangumi_demo.py
[video]: https://github.com/dolaCmeo/acfunsdk/blob/main/examples/video_demo.py
[article]: https://github.com/dolaCmeo/acfunsdk/blob/main/examples/article_demo.py
[album]: https://github.com/dolaCmeo/acfunsdk/blob/main/examples/album_demo.py
[member]: https://github.com/dolaCmeo/acfunsdk/blob/main/examples/member_demo.py
[moment]: https://github.com/dolaCmeo/acfunsdk/blob/main/examples/moment_demo.py
[live]: https://github.com/dolaCmeo/acfunsdk/blob/main/examples/live_demo.py

[saver]: https://github.com/dolaCmeo/acfunsdk/blob/main/examples/AcSaver_demo.py
