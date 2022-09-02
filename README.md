# acfunSDK - **UNOFFICEICAL**

_Developing..._
- - -

acfunSDK是 **非官方的 [AcFun弹幕视频网][acfun.cn]** Python库。

几乎搜集了所有与 [AcFun弹幕视频网][acfun.cn] 相关的接口与数据。

ps: _只要项目还没有弃坑，如发现未知接口，或现有功能失效，请随时提交 [Issue]_

- - -

## 环境依赖

**Python** : 开发环境为 `Python 3.8.10` & `Python 3.9.6`

理论向上任意兼容，向下兼容情况不明。
`Python`本体请自行[下载安装][python]。


**安装依赖** : _建议使用[虚拟环境][venv]_
```sh
pip install -r requirements.txt
```
- - -

## 使用方法


### 实例化获取对象
```python
from acfun import Acer
# 实例化一个Acer
acer = Acer(debug=True)
# 登录用户(成功登录后会自动保存 '<用户名>.cookies')
acer.login(username='you@email.com', password='balalabalala')
# 读取用户(读取成功登录后保存的 '<用户名>.cookies')
acer.loading(username='13800138000')
# 每日签到，领香蕉🍌
acer.signin()
# 通过连接直接获取内容对象
# 目前支持 9种类型：
# 视  频: https://www.acfun.cn/v/ac4741185
demo_video = acer.get("https://www.acfun.cn/v/ac4741185")
print(demo_video)
# 文  章: https://www.acfun.cn/a/ac16695813
demo_article = acer.get("https://www.acfun.cn/v/ac4741185")
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
待补充

</details>

<details>
<summary>AcSaver</summary>

> 这是一个依赖acfunSDK的小工具，也算是DEMO。
> 
> 主要用于离线收藏保存A站的各种资源。
> 保存后，可使用浏览器打开对应页面。

**需要ffmpeg**
> `ffmpeg` 主要用于下载视频。
> 
> 建议去官网下载 https://ffmpeg.org/download.html
>
> 可执行文件 `ffmpeg` 需要加入到环境变量，或复制到运行根目录。


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
demo_article = acer.get("https://www.acfun.cn/v/ac4741185")
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

内置+修改: 位于 `libs` 文件夹内

+ [`you-get`](https://github.com/soimort/you-get)
+ [`ffmpeg_progress_yield`](https://github.com/slhck/ffmpeg-progress-yield)

依赖: 包含在 `requirements.txt` 中

+ [`rich`](https://pypi.org/project/rich/)
+ [`arrow`](https://pypi.org/project/arrow/)
+ [`pycryptodome`](https://pypi.org/project/pycryptodome/)
+ [`jinja2`](https://pypi.org/project/jinja2/)

+ [`psutil`](https://pypi.org/project/psutil/)
+ [`filetype`](https://pypi.org/project/filetype/)
+ [`pyperclip`](https://pypi.org/project/pyperclip/)
+ [`alive-progress`](https://pypi.org/project/alive-progress/)
+ [`m3u8`](https://pypi.org/project/m3u8/)
+ [`httpx`](https://pypi.org/project/httpx/)
+ [`websocket-client`](https://pypi.org/project/websocket-client/)

+ [`beautifulsoup4`](https://pypi.org/project/beautifulsoup4/)
+ [`cssutils`](https://pypi.org/project/cssutils/)
+ [`lxml`](https://pypi.org/project/lxml/)
+ [`js2py`](https://pypi.org/project/js2py/)

+ [`protobuf`](https://pypi.org/project/protobuf/)
+ [`proto-plus`](https://pypi.org/project/proto-plus/)
+ [`blackboxprotobuf`](https://pypi.org/project/blackboxprotobuf/)
</details>

- - - 
## 参考 & 鸣谢

+ [AcFun 助手](https://github.com/niuchaobo/acfun-helper) 是一个适用于 AcFun（ acfun.cn ） 的浏览器插件。
+ [AcFunDanmaku](https://github.com/wpscott/AcFunDanmaku) 是用C# 和 .Net 6编写的AcFun直播弹幕工具。
+ [实现自己的AcFun直播弹幕姬](https://www.acfun.cn/a/ac16695813) [@財布士醬](https://www.acfun.cn/u/311509)
+ QQ频道“AcFun开源⑨课”

- - - 

## About Me

![AcFunCard](https://discovery.sunness.dev/39088)

- - - 

[acfun.cn]: https://www.acfun.cn/
[Issue]: https://github.com/dolaCmeo/acfunSDK/issues
[python]: https://www.python.org/downloads/
[venv]: https://docs.python.org/zh-cn/3.8/library/venv.html
