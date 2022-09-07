# coding=utf-8
import json
import re
from bs4 import BeautifulSoup as Bs
from acfun.source import routes, apis
from acfun.page.utils import thin_string, match1
from acfun.exceptions import *

__author__ = 'dolacmeo'


class Moment:
    raw_data = dict()
    like_count = 0
    banana_count = 0
    comment_count = 0
    linked = None

    def __init__(self, acer, raw_data: dict):
        self.acer = acer
        self.raw_data = raw_data
        if self.tag_rtype in [1, 2, 3, 10]:
            if self.rtype == 3:
                self.linked = self.acer.AcArticle(self.rid)
            elif self.rtype == 2:
                self.linked = self.acer.AcVideo(self.rid)
            elif self.rtype == 10:
                rsource = self.raw_data.get('repostSource')
                if rsource is not None:
                    self.linked = Moment(self.acer, self.raw_data.get('repostSource'))

    @property
    def tag_rtype(self):
        return self.raw_data.get('tagResourceType')

    @property
    def rtype(self):
        return self.raw_data.get('resourceType')

    @property
    def rid(self):
        return self.raw_data.get('resourceId')

    @property
    def mtype(self):
        return self.raw_data.get('momentType')

    def __repr__(self):
        if self.tag_rtype in [1, 2, 10]:
            name = self.raw_data.get('user', {}).get('userName', '')
            return f"AcMoment(@{name} | {str(self.linked)})".encode(errors='replace').decode()
        elif self.tag_rtype == 3:
            name = self.raw_data.get('user', {}).get('userName', '')
            text = self.raw_data.get('moment', {}).get('replaceUbbText', '')
            # text = re.sub('\[emot=acfun,\d+/]', '', thin_string(text))
            text = thin_string(text)
            img_count = self.raw_data.get('discoveryResourceFeedShowImageCount', 0)
            img_count = f"【图x{img_count}】" if img_count > 0 else ""
            link = "" if self.linked is None else f" | {str(self.linked)}"
            return f"AcMoment(@{name}: {img_count}{text}{link})".encode(errors='replace').decode()
        return f"AcMoment()"

    def up(self):
        return self.acer.AcUp(self.raw_data.get('user'))

    def comment(self):
        return self.acer.AcComment(self.rid, self.rtype, self)

    @need_login
    def banana(self, count: int):
        return self.acer.throw_banana(self.rid, self.rtype, count)


class AcMoment:
    cursor = "0"
    limit = 10
    moment_data = list()
    resourceTypes = 0
    rts = {  # 0综合 2视频 3文章 10动态
        'all': 0,
        'video': 2,
        'article': 3,
        'moment': 10
    }

    def __init__(self, acer):
        self.acer = acer

    @need_login
    def set_tab(self, tab: str = 'all'):
        new = self.rts.get(tab, 0)
        if new != self.resourceTypes:
            self.resourceTypes = new
            self.cursor = "0"
            self.moment_data = list()
            return True
        return False

    @need_login
    def feed(self, limit: int = 10, refresh: bool = False):
        if refresh is True:
            self.cursor = "0"
            self.moment_data = list()
        param = {
            "useWebp": False,
            "pcursor": self.cursor,
            "count": limit or self.limit,
            "resourceTypes": self.resourceTypes,
        }
        api_req = self.acer.client.get(apis['follow_feed'], params=param)
        api_data = api_req.json()
        if api_data.get('result') == 0:
            self.cursor = api_data.get('pcursor', self.cursor)
            self.moment_data.extend(api_data.get('feedList', []))
        return [Moment(self.acer, x) for x in api_data.get('feedList', [])]

    def get(self, am_num: [str, int]):
        page_req = self.acer.client.get(f"{routes['moment']}{am_num}")
        json_text = match1(page_req.text, r"(?s)__INITIAL_STATE__\s*=\s*(\{.*?\});")
        page_data = json.loads(json_text).get('moment', {}).get('moment')
        return Moment(self.acer, page_data)

