# coding=utf-8
from .utils import math
from .utils import AcSource, need_login, ms2time

__author__ = 'dolacmeo'


class AcDanmaku:
    ac_num = None
    vid = None
    danmaku_data = list()

    def __init__(self, acer, video_id: int, parent):
        self.acer = acer
        self.vid = video_id
        self.parent = parent
        self._get_all_danmaku()

    def __repr__(self):
        return f"AcDanmaku([{self.vid}] Σ{len(self.danmaku_data)})"

    def _get_data(self, page=1, limit=200, sorttype=2, asc=True):
        param = {
            "resourceId": f"{self.vid}",
            "resourceType": "9",
            "enableAdvanced": True,
            "pcursor": f"{page}",
            "count": f"{limit}",
            "sortType": f"{sorttype}",
            "asc": asc,
        }
        api_req = self.acer.client.get(AcSource.apis['danmaku'], params=param)
        api_data = api_req.json()
        if api_data.get("result") == 11:
            api_req = self.acer.client.get(AcSource.apis['danmaku_lab'], params=param)
            api_data = api_req.json()
        return api_data

    def _get_all_danmaku(self):
        self.danmaku_data = list()
        limit = 200
        page = 1
        more = 1
        while more > 0:
            api_data = self._get_data(page)
            total = api_data.get('totalCount', 1)
            self.danmaku_data.extend(api_data.get('danmakus', []))
            more = math.ceil(total / limit) - page
            page += 1

    def list(self):
        return [Danmaku(self.acer, self.vid, x, self.parent) for x in self.danmaku_data]

    @need_login
    def add(self, words, ms, color=16777215, mode=1, size=25):
        danmaku = {
            "size": size,  # 大* 中25 小16
            "mode": mode,
            "color": color,
            "position": ms,
            "body": words,
            "type": "bangumi" if self.parent._objname == "AcBangumi" else "douga",
            "videoId": self.vid,
            "id": self.parent.resource_id,
            "subChannelId": self.parent.raw_data.get("channel", {}).get('id'),
            "subChannelName": self.parent.raw_data.get("channel", {}).get('name'),
            "roleId": ""
        }
        req = self.acer.client.post(AcSource.apis['danmaku_add'],
                                    data=danmaku, headers={"referer": f"{AcSource.routes['index']}"})
        return req.json().get('result') == 0


class Danmaku:
    data = dict()
    video_data = dict()
    ac_num = None
    vid = None
    isLike = None

    def __init__(self, acer, video_id: int, data: dict, parent):
        self.acer = acer
        self.vid = video_id
        self.data = data
        self.parent = parent

    @property
    def userId(self):
        return self.data.get('userId')

    @property
    def position(self):
        return self.data.get('position')

    @property
    def body(self):
        return self.data.get('body')

    @property
    def danmakuId(self):
        return self.data.get('danmakuId')

    def __repr__(self):
        return f"DM([{ms2time(self.position)}]#{self.danmakuId} {self.body} @{self.userId})"

    def up(self):
        return self.acer.acfun.AcUp(self.userId)

    @need_login
    def like(self):
        req = self.acer.client.post(AcSource.apis['danmaku_like'], params={"danmakuId": self.danmakuId})
        self.isLike = req.json().get('result') == 0
        return self.isLike is True

    @need_login
    def like_cancel(self):
        req = self.acer.client.post(AcSource.apis['danmaku_like_cancel'], params={"danmakuId": self.danmakuId})
        self.isLike = not (req.json().get('result') == 0)
        return self.isLike is False

    @need_login
    def block_words(self, word=None):
        req = self.acer.client.post(AcSource.apis['danmaku_block_add'], params={
            "blockWordsType": 1,
            "blockWords": word or self.body
        })
        return req.json().get('result') == 0

    @need_login
    def block_acer(self):
        req = self.acer.client.post(AcSource.apis['danmaku_block_add'], params={
            "blockWordsType": 2,
            "blockWords": self.userId
        })
        return req.json().get('result') == 0

    @need_login
    def block_words_delete(self):
        req = self.acer.client.post(AcSource.apis['danmaku_block_delete'], params={
            "blockWordsType": 1,
            "blockWordsList": self.body
        })
        return req.json().get('result') == 0

    @need_login
    def block_acer_delete(self):
        req = self.acer.client.post(AcSource.apis['danmaku_block_delete'], params={
            "blockWordsType": 2,
            "blockWordsList": self.userId
        })
        return req.json().get('result') == 0

    @need_login
    def report(self):
        req = self.acer.client.post(AcSource.apis['danmaku_block_delete'], params={
            "reportedUserId": self.userId,
            "danmakuId": self.danmakuId,
            "body": self.body,
            "type": "douga",
            "id": self.parent.resource_id,
            "videoId": self.vid,
            "subChannelId": self.parent.raw_data.get("channel", {}).get('id'),
            "subChannelName": self.parent.raw_data.get("channel", {}).get('name'),
        })
        return req.json().get('result') == 0
