# acfunSDK - **UNOFFICEICAL**

<br />

<p align="center">
<a href="https://github.com/dolaCmeo/acfunSDK">
<img height="100" src="https://s3.dualstack.us-east-2.amazonaws.com/pythondotorg-assets/media/files/python-logo-only.svg" alt="">
<img height="100" src="https://ali-imgs.acfun.cn/kos/nlav10360/static/common/widget/header/img/acfunlogo.11a9841251f31e1a3316.svg" alt="">
</a>
</p>

<br />

acfunSDK是 **非官方的 [AcFun弹幕视频网][acfun.cn]** Python库。

几乎搜集了所有与 [AcFun弹幕视频网][acfun.cn] 相关的接口与数据。

ps: _如发现未知接口，或现有功能失效，请随时提交 [Issue]_

- - -

**Python** : 开发环境为 `Python 3.8.10` & `Python 3.9.6`

`Python`本体请自行[下载安装][python]。

## [从PyPI安装](https://pypi.org/project/acfunsdk/)

```shell
python -m pip install acfunsdk
```

**需要`ffmpeg`**  主要用于下载视频。
> 建议去官网下载 https://ffmpeg.org/download.html
>
> 可执行文件 `ffmpeg` 需要加入到环境变量，或复制到运行根目录。

- - -

## 使用方法


### 实例化获取对象
```python
from acfun import Acer
# 实例化一个Acer
acer = Acer(debug=True)
# 登录用户(成功登录后会自动保存 '<用户名>.cookies')
# 请注意保存，防止被盗
acer.login(username='you@email.com', password='balalabalala')
# 读取用户(读取成功登录后保存的 '<用户名>.cookies')
acer.loading(username='13800138000')
# 每日签到，领香蕉🍌
acer.signin()
# 通过链接直接获取内容对象
# 目前支持 9种类型：
# 视  频: https://www.acfun.cn/v/ac4741185
demo_video = acer.get("https://www.acfun.cn/v/ac4741185")
print(demo_video)
# 文  章: https://www.acfun.cn/a/ac16695813
demo_article = acer.get("https://www.acfun.cn/a/ac16695813")
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
```

- - -

<details>
<summary>DEMOs</summary>

**以下DEMO列举了主要的使用方法，具体请自行研究。**

## 👤 主要对象

+ 主对象acer示例 [acer_demo.py][acer] 

## 📖 综合页面对象

+ 首页对象示例 [index_reader.py][index] 
+ 频道对象示例 [channel_reader.py][channel] 
+ 搜索对象示例 [search_reader.py][search] 

## 🔗 内容页面对象

+ 番剧对象 [bangumi_demo.py][bangumi]
+ 视频对象 [video_demo.py][video]
+ 文章对象 [article_demo.py][article]
+ 合集对象 [album_demo.py][album]
+ UP主对象 [member_demo.py][member]
+ 动态对象 [moment_demo.py][moment]
+ 直播对象 [live_demo.py][live]

## 🎁 附赠: AcSaver

+ 离线保存 [AcSaver_demo.py][saver] 

</details>

<details>
<summary>AcSaver</summary>

> 这是一个依赖acfunSDK的小工具，也算是DEMO。
> 
> 主要用于离线收藏保存A站的各种资源。
> 保存后，可使用浏览器打开对应页面。


初始化本地路径
```python
saver_path = r"D:\AcSaver"

# 实例化AcSaver父类
acsaver = acer.AcSaver(saver_path)
# 实例化后 会在路径下生成 index.html

# github下载静态文件
# https://github.com/dolaCmeo/acfunSDK/tree/assets
acsaver.download_assets_from_github()

# 下载所有Ac表情资源
acsaver.save_emot()
```

保存文章
```python
demo_article = acer.get("https://www.acfun.cn/a/ac32633020")
demo_article.saver(saver_path).save_all()
```

保存视频
```python
demo_video = acer.get("https://www.acfun.cn/v/ac4741185")
demo_video.saver(saver_path).save_all()
```

~~保存番剧(暂未支持)~~
```python

```

~~录制直播(暂未支持)~~
```python

```

</details>

<details>
<summary>依赖库</summary>

>内置+修改: 位于 `libs` 文件夹内
>
>+ [`ffmpeg_progress_yield`](https://github.com/slhck/ffmpeg-progress-yield)
>+ [`blackboxprotobuf`](https://pypi.org/project/blackboxprotobuf/)

**依赖: 包含在 `requirements.txt` 中**

基础网络请求及页面解析:
+ [`httpx`](https://pypi.org/project/httpx/)`>=0.23`
+ [`lxml`](https://pypi.org/project/lxml/)`>=4.9`
+ [`beautifulsoup4`](https://pypi.org/project/beautifulsoup4/)`>=4.11`
+ [`cssutils`](https://pypi.org/project/cssutils/)`>=2.6`

下载及html页面渲染:
+ [`alive-progress`](https://pypi.org/project/alive-progress/)`>=2.4`
+ [`filetype`](https://pypi.org/project/filetype/)`>=1.1`
+ [`jinja2`](https://pypi.org/project/jinja2/)`>=3.1`

WebSocket通信及数据处理:
+ [`websocket-client`](https://pypi.org/project/websocket-client/)`>=1.4`
+ [`pycryptodome`](https://pypi.org/project/pycryptodome/)`>=3.15`
+ [`protobuf`](https://pypi.org/project/protobuf/)`==3.20.1`
+ [`proto-plus`](https://pypi.org/project/proto-plus/)`==1.22.1`
+ [`rich`](https://pypi.org/project/rich/)`>=12.5`
+ [`psutil`](https://pypi.org/project/psutil/)`>=5.9`

</details>

- - - 
## 参考 & 鸣谢

+ [AcFun 助手](https://github.com/niuchaobo/acfun-helper) 是一个适用于 AcFun（ acfun.cn ） 的浏览器插件。
+ [AcFunDanmaku](https://github.com/wpscott/AcFunDanmaku) 是用C# 和 .Net 6编写的AcFun直播弹幕工具。
+ [实现自己的AcFun直播弹幕姬](https://www.acfun.cn/a/ac16695813) [@財布士醬](https://www.acfun.cn/u/311509)
+ QQ频道“AcFun开源⑨课”
+ 使用 [Poetry](https://python-poetry.org/) 构建

- - - 

## About Me

[![ac彩娘-阿部高和](https://tx-free-imgs2.acfun.cn/kimg/bs2/zt-image-host/ChQwODliOGVhYzRjMTBmOGM0ZWY1ZRCIzNcv.gif)][dolacfun]
♂ 整点大香蕉🍌
<img alt="AcFunCard" align="right" src="https://discovery.sunness.dev/39088">

- - - 

[dolacfun]: https://www.acfun.cn/u/39088

[acfun.cn]: https://www.acfun.cn/
[Issue]: https://github.com/dolaCmeo/acfunSDK/issues
[python]: https://www.python.org/downloads/
[venv]: https://docs.python.org/zh-cn/3.8/library/venv.html

[acer]: https://github.com/dolaCmeo/acfunSDK/blob/main/examples/acer_demo.py
[index]: https://github.com/dolaCmeo/acfunSDK/blob/main/examples/index_reader.py
[channel]: https://github.com/dolaCmeo/acfunSDK/blob/main/examples/channel_reader.py
[search]: https://github.com/dolaCmeo/acfunSDK/blob/main/examples/seach_reader.py

[bangumi]: https://github.com/dolaCmeo/acfunSDK/blob/main/examples/bangumi_demo.py
[video]: https://github.com/dolaCmeo/acfunSDK/blob/main/examples/video_demo.py
[article]: https://github.com/dolaCmeo/acfunSDK/blob/main/examples/article_demo.py
[album]: https://github.com/dolaCmeo/acfunSDK/blob/main/examples/album_demo.py
[member]: https://github.com/dolaCmeo/acfunSDK/blob/main/examples/member_demo.py
[moment]: https://github.com/dolaCmeo/acfunSDK/blob/main/examples/moment_demo.py
[live]: https://github.com/dolaCmeo/acfunSDK/blob/main/examples/live_demo.py

[saver]: https://github.com/dolaCmeo/acfunSDK/blob/main/examples/AcSaver_demo.py
