# coding=utf-8
import os
import re
import json
import time
import math
import httpx
import base64
import subprocess
from uuid import uuid4
from urllib import parse
from typing import Literal
from datetime import timedelta
from bs4 import BeautifulSoup as Bs
from bs4.element import Tag
from ..source import AcSource
from ..exceptions import need_login, not_404

__author__ = 'dolacmeo'

resource_type_map = {
    "1": "AcBangumi",  # 番剧
    "2": "AcVideo",  # 视频稿件
    "3": "AcArticle",  # 文章稿件
    "4": "AcAlbum",  # 合辑
    "5": "AcUp",  # 用户
    "6": "AcComment",  # 评论
    # "8": "私信",
    "10": "AcMoment",  # 动态
}

routes_type_map = {
    "bangumi": "AcBangumi",  # 番剧
    "video": "AcVideo",  # 视频稿件
    "article": "AcArticle",  # 文章稿件
    "album": "AcAlbum",  # 合辑
    "up": "AcUp",  # 用户
    "live": "AcLiveUp",  # 用户直播
    "moment": "AcMoment",  # 用户动态
    "doodle": "AcDoodle",  # 涂鸦页面
}

type_routes_map = {v: k for k, v in routes_type_map.items()}

resource_type_str_map = {
    "1": "番剧",  # AcBangumi
    "2": "视频",  # AcVideo
    "3": "文章",  # AcArticle
    "4": "合辑",  # AcAlbum
    "5": "用户",  # AcUp
    "6": "评论",  # AcComment
    "10": "动态",  # AcMoment
}

acpage_regex = {
    "AcBangumi": [
        r"(?s)bangumiData\s*=\s*(\{.*?\});",
        r"(?s)bangumiList\s*=\s*(\{.*?\});"
    ],  # 番剧
    "AcVideo": [r"(?s)videoInfo\s*=\s*(\{.*?\});"],  # 视频稿件
    "AcArticle": [r"(?s)articleInfo\s*=\s*(\{.*?\});"],  # 文章稿件
    "AcAlbum": [r"(?s)__INITIAL_STATE__\s*=\s*(\{.*?\});"],  # 合辑
    "AcMoment": [r"(?s)__INITIAL_STATE__\s*=\s*(\{.*?\});"],  # 动态
    "AcDoodle": [r"(?s)__schema__\s*=\s*'(\{.*?\})';"],  # 涂鸦页面
    "AcUp": [],  # 用户
}


class VideoItem:
    raw_data = None

    def __init__(self, acer, video_id: int, sub_title: str, referer: str, parent):
        self.acer = acer
        self.vid = video_id
        self.sub_title = sub_title
        self.referer = referer
        self.parent = parent
        self.loading()

    def __repr__(self):
        return f"{self.parent}"

    def _get_data_from_quick_view(self) -> (dict, None):
        param = {"quickViewId": "videoInfo_new", "ajaxpipe": 1}
        page_req = self.acer.client.get(self.referer, params=param)
        assert page_req.text.endswith("/*<!-- fetch-stream -->*/")
        page_data = json.loads(page_req.text[:-25])
        v_script = match1(page_data['html'].replace(" ", ""), r"videoInfo=((?=\{)[^\s]*(?<=\}));?")
        video_data = json.loads(v_script)
        return video_data.get("currentVideoInfo")

    def _get_data_from_api(self) -> (dict, None):
        param = {
            "resourceId": self.parent.resource_id,
            "resourceType": self.parent.resource_type,
            "videoId": self.vid
        }
        api_req = self.acer.client.get(AcSource.apis['video_ksplay'], params=param)
        api_data = api_req.json()
        assert api_data.get('result') == 0
        return api_data.get("playInfo")

    @property
    def quality(self) -> list:
        return self.raw_data.get("transcodeInfos", [])

    def m3u8_url(self, quality: [int, str] = 0, hevc: bool = True, only_url: bool = True) -> (dict, str, None):
        if isinstance(quality, int):
            assert quality in range(len(self.quality))
        elif isinstance(quality, str):
            quality = quality.lower()
            q_map = {x["qualityType"]: i for i, x in enumerate(self.quality)}
            assert quality in q_map.keys()
            quality = q_map[quality]
        else:
            return None
        code_type = "ksPlayJsonHevc" if hevc is True else "ksPlayJson"
        play_data = json.loads(self.raw_data.get(code_type, ""))
        this_quality = play_data.get("adaptationSet", [{}])[0].get("representation")[quality]
        domains = self.raw_data.get("domainInfos", [])
        if len(domains):
            main_url = parse.urlsplit(this_quality['url'])
            this_quality['backupUrl'] = list()
            for domain in domains:
                new_url = f"{main_url.scheme}://{domain['url']}{main_url.path}?{main_url.query}"
                this_quality['backupUrl'].append(new_url)
        if only_url is True:
            return this_quality['url'], this_quality['backupUrl']
        return this_quality

    def play(self, potplayer_path: [os.PathLike, str], quality: [int, str] = "1080p", hevc: bool = True):
        assert os.path.exists(potplayer_path)
        adapt = self.m3u8_url(quality, hevc, False)
        qtype = adapt["qualityType"]
        quality_mark = f"{qtype}_HEVC" if hevc is True else qtype
        title = f"-{self.sub_title}" if len(self.sub_title) else ""
        player_title = f'"{self.parent}{title}-{quality_mark}"'.replace(" ", '')
        cmds = [potplayer_path, adapt['url'], "/title", emoji_cleanup(player_title)]
        return subprocess.Popen(cmds, stdout=subprocess.PIPE)

    @property
    def scenes(self) -> (dict, None):
        form_data = {
            "resourceId": self.parent.resource_id,
            "resourceType": self.parent.resource_type,
            "videoId": self.vid
        }
        api_req = self.acer.client.post(AcSource.apis['video_scenes'], data=form_data)
        api_data = api_req.json()
        if api_data.get('result') != 0:
            return None
        if api_data.get("spriteVtt") is None:
            return None
        pos_data = list()
        sprite_data = api_data.get("spriteVtt", "").split("\n\n")[1:]
        sprite_img = sprite_data[0].split("\n")[1].split("#")[0]
        for line in sprite_data:
            pos, img_url = line.split("\n")
            pos_s, pos_e = pos.split(" --> ")
            _, xywh = img_url.split("#xywh=")
            pos_data.append([pos_s, pos_e, xywh])
        return {"sprite_image": sprite_img, "pos": pos_data}

    @property
    def hotspot(self) -> (dict, None):
        form_data = {
            "resourceId": self.parent.resource_id,
            "resourceType": self.parent.resource_type
        }
        api_req = self.acer.client.post(AcSource.apis['video_hotspot'], data=form_data)
        api_data = api_req.json()
        if api_data.get('result') != 0:
            return None
        return api_data.get("hotSpotDistribution")

    def loading(self):
        self.raw_data = self._get_data_from_api()

    @property
    def danmaku(self) -> object:
        return self.acer.acfun.AcDanmaku(self.vid, self.parent)


class AcDetail:
    resource_type = None
    resource_id = None
    is_404 = False
    raw_data = dict()
    page_text = None
    page_obj = None
    pagelets = list()
    __funcs = {
        "AcBangumi": ['get_video', 'comment', 'like', 'favorite', 'banana'],
        "AcVideo":   ['up', 'up_uid', 'up_name', 'get_video', 'comment', 'like', 'favorite', 'banana'],
        "AcArticle": ['up', 'up_uid', 'up_name', 'comment', 'like', 'favorite', 'banana'],
        "AcAlbum":   ['favorite'],
        "AcMoment":  ['up', 'up_uid', 'up_name', 'comment', 'like', 'banana'],
        "AcDoodle":  ['comment']
    }
    _msg = {
        "404": "咦？世界线变动了。看看其他内容吧~"
    }

    def __init__(self, acer, rtype: [str, int], rid: [str, int]):
        self.acer = acer
        self.resource_type = int(rtype)
        self.resource_id = int(rid)
        self.loading()

    @property
    def _objname(self):
        return self.__class__.__name__

    @property
    def referer(self):
        route_name = type_routes_map[self._objname]
        return f"{AcSource.routes[route_name]}{self.resource_id}"

    @property
    def qrcode(self):
        parma = {
            "content": self.referer,
            "contentType": "URL",
            "toShortUrl": False,
            "width": 100,
            "height": 100
        }
        return f"{AcSource.apis['qrcode']}?{parse.urlencode(parma)}"

    @property
    def title(self):
        return ""

    def __repr__(self):
        if self.is_404:
            return f"{self._objname}([#{self.resource_id}]咦？世界线变动了。看看其他内容吧~)"
        return f"{self._objname}([#{self.resource_id}]{self.title})"

    def loading(self):
        req = self.acer.client.get(self.referer)
        self.is_404 = req.status_code // 100 != 2
        if self.is_404:
            return False
        self.page_text = req.text
        self.page_obj = Bs(req.text, 'lxml')
        self.pagelets = get_page_pagelets(self.page_obj)
        rex = acpage_regex.get(self._objname, [])
        if self._objname == "AcBangumi":
            script_bangumidata, script_bangumilist = match1(req.text, *rex)
            self.raw_data = dict(data=json.loads(script_bangumidata), list=json.loads(script_bangumilist))
        elif len(rex):
            self.raw_data = json.loads(match1(req.text, *rex))
        if "ssrContext" in self.raw_data.keys():
            route_name = type_routes_map[self._objname]
            self.raw_data = self.raw_data.get(route_name)
        if self._objname in self.__funcs.keys():
            for k in self.__funcs[self._objname]:
                self.__setattr__(k, getattr(self, f"_{k}"))
        self.loading_more()

    def loading_more(self):
        pass

    @property
    @not_404
    def _up_uid(self):
        user = self.raw_data.get('user', {})
        return user.get("id")

    @property
    @not_404
    def _up_name(self):
        user = self.raw_data.get('user', {})
        return user.get("name", "")

    @not_404
    def _up(self):
        return self.acer.acfun.AcUp(self._up_uid)

    @not_404
    def _get_video(self, video_id: int, sub_title: str, referer: str):
        return VideoItem(self.acer, video_id, sub_title, referer, self)

    @not_404
    def _comment(self) -> object:
        return self.acer.acfun.AcComment(self.resource_type, self.resource_id)

    @not_404
    def _like(self, on_off: bool):
        if on_off is True:
            return self.acer.like_add(self.resource_type, self.resource_id)
        return self.acer.like_delete(self.resource_type, self.resource_id)

    @not_404
    def _favorite(self, on_off: bool):
        if on_off is True:
            return self.acer.favourite.add(self.resource_type, self.resource_id)
        return self.acer.favourite.cancel(self.resource_type, self.resource_id)

    @not_404
    def _banana(self, count: int):
        assert 1 >= count >= 5
        return self.acer.throw_banana(self.resource_type, self.resource_id, count)

    @not_404
    def report(self, crime: str, proof: str, description: str):
        return self.acer.acfun.AcReport.submit(
            self.referer, self.resource_type, self.resource_id, self._up_uid,
            crime, proof, description)


class B64s:
    STANDARD = b'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
    EN_TRANS = STANDARD
    DE_TRANS = STANDARD

    def __init__(self, s: [bytes, bytearray], n: [int, None] = None):
        self.raw = s
        if isinstance(n, int):
            n = n % 64
            new = self.STANDARD[n:] + self.STANDARD[:n]
            self.EN_TRANS = bytes.maketrans(self.STANDARD, new)
            self.DE_TRANS = bytes.maketrans(new, self.STANDARD)

    def b64encode(self):
        return base64.standard_b64encode(self.raw).translate(self.EN_TRANS)

    def b64decode(self):
        return base64.b64decode(self.raw.translate(self.DE_TRANS))


def sizeof_fmt(num, suffix="B") -> str:
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f} {unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f} Yi{suffix}"


def match_info(text) -> (dict, None):
    rex = re.compile(r"(?P<title>.*)\r"
                     r"UP:(?P<up>.*)\r"
                     r"发布于(?P<createTime>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})"
                     r"\xa0/\xa0点击:(?P<viewCount>\d+)"
                     r"\xa0/\xa0评论:(?P<commentCount>\d+)")
    result = rex.fullmatch(text)
    if result is None:
        return None
    return result.groupdict()


def match1(text, *patterns):
    """Scans through a string for substrings matched some patterns (first-subgroups only).

    Args:
        text: A string to be scanned.
        patterns: Arbitrary number of regex patterns.

    Returns:
        When only one pattern is given, returns a string (None if no match found).
        When more than one pattern are given, returns a list of strings ([] if no match found).
    """

    if len(patterns) == 1:
        pattern = patterns[0]
        match = re.search(pattern, text)
        if match:
            return match.group(1)
        else:
            return None
    else:
        ret = []
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                ret.append(match.group(1))
        return ret


def matchall(text, patterns):
    """Scans through a string for substrings matched some patterns.

    Args:
        text: A string to be scanned.
        patterns: a list of regex pattern.

    Returns:
        a list if matched. empty if not.
    """

    ret = []
    for pattern in patterns:
        match = re.findall(pattern, text)
        ret += match

    return ret


def emoji_cleanup(text) -> str:
    # Ref: https://gist.github.com/Alex-Just/e86110836f3f93fe7932290526529cd1#gistcomment-3208085
    # Ref: https://en.wikipedia.org/wiki/Unicode_block
    EMOJI_PATTERN = re.compile(
        "(["
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F700-\U0001F77F"  # alchemical symbols
        "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
        "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U0001FA00-\U0001FA6F"  # Chess Symbols
        "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        "\U00002702-\U000027B0"  # Dingbats
        "])"
    )
    text = re.sub(EMOJI_PATTERN, r'', text)
    return text


def image_uploader(client, image_data: bytes, ext: str = 'jpeg') -> str:
    token_req = client.post(AcSource.apis['image_upload_gettoken'], data=dict(fileName=uuid4().hex.upper() + f'.{ext}'))
    token_data = token_req.json()
    assert token_data.get('result') == 0
    resume_req = client.get(AcSource.apis['image_upload_resume'], params=dict(upload_token=token_data['info']['token']))
    resume_data = resume_req.json()
    assert resume_data.get('result') == 1
    fragment_req = client.post(AcSource.apis['image_upload_fragment'], data=image_data,
                               params=dict(upload_token=token_data['info']['token'], fragment_id=0),
                               headers={"Content-Type": "application/octet-stream"})
    fragment_data = fragment_req.json()
    assert fragment_data.get('result') == 1
    complete_req = client.post(AcSource.apis['image_upload_complete'],
                               params=dict(upload_token=token_data['info']['token'], fragment_count=1))
    complete_data = complete_req.json()
    assert complete_data.get('result') == 1
    result_req = client.post(AcSource.apis['image_upload_geturl'], data=dict(token=token_data['info']['token']))
    result_data = result_req.json()
    assert result_data.get('result') == 0
    return result_data.get('url')


def limit_string(s, n) -> str:
    s = s[:n]
    if len(s) == n:
        s = s[:-2] + "..."
    return s


def thin_string(_string: str, no_break: bool = False) -> str:
    final_str = list()
    for line in _string.replace('\r', '').split('\n'):
        new_line = ' '.join(line.split()).strip()
        if len(new_line):
            final_str.append(new_line)
    if no_break is True:
        return " ".join(final_str)
    return " ↲ ".join(final_str)


def warp_mix_chars(_string: str, lens: int = 40, border: [tuple, None] = None) -> (str, list):
    output = list()
    tmp_string = ""
    tmp_count = 0
    for i, _char in enumerate(_string):
        char_count = 2 if '\u4e00' <= _char <= '\u9fcc' else 1
        if tmp_count + char_count > lens:
            tmp_string += ' ' * (lens - tmp_count)
            output.append(tmp_string)
            tmp_string = ""
            tmp_count = 0
        tmp_string += _char
        tmp_count += char_count
    if tmp_count != 0:
        tmp_string += ' ' * (lens - tmp_count)
        output.append(tmp_string)
    if isinstance(border, tuple) and len(border) == 2:
        output = [f"{border[0]}{x}{border[1]}" for x in output]
    return output


def ms2time(ms: int) -> str:
    d = timedelta(milliseconds=ms)
    return str(d).split('.')[0]


def get_page_pagelets(page_obj) -> list:
    data = list()
    for item in page_obj.select("[id^=pagelet_]"):
        data.append(item.attrs['id'])
    if len(data):
        data.append('footer')
    return data


def url_complete(url) -> str:
    if isinstance(url, str):
        if url.startswith('//'):
            url = f"https:{url}"
        elif not url.startswith('http'):
            url = f"{AcSource.routes['index']}{url}"
    return url


def get_dict_value_in_path(data: dict, path: [str, list], default=None):
    if isinstance(path, str):
        path = path.split('.')
    inside = data
    for i, x in enumerate(path):
        v = default if i == len(path) - 1 else {}
        inside = inside.get(x, v)
    return inside
