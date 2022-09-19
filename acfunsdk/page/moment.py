# coding=utf-8
import json
from acfunsdk.source import routes, apis
from acfunsdk.page.utils import thin_string, limit_string, match1

__author__ = 'dolacmeo'


class AcMoment:
    resource_type = 10
    raw_data = dict()
    like_count = 0
    banana_count = 0
    comment_count = 0
    linked = None

    def __init__(self, acer, am_num: [int, str]):
        self.acer = acer
        self.am_num = int(am_num)
        self.loading()
        if self.rtype in range(1, 5):
            self.linked = self.acer.acfun.resource(self.rtype, self.rid)
        elif self.rtype == 10:
            rsource = self.raw_data.get('repostSource')
            if rsource is not None:
                self.linked = AcMoment(self.acer, self.raw_data.get('repostSource'))

    def loading(self):
        page_req = self.acer.client.get(f"{routes['moment']}{self.am_num}")
        json_text = match1(page_req.text, r"(?s)__INITIAL_STATE__\s*=\s*(\{.*?\});")
        self.raw_data = json.loads(json_text).get('moment', {}).get('moment')

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

    @property
    def text_without_ubb(self):
        return self.raw_data.get("replaceUbbText")

    def __repr__(self):
        if self.tag_rtype is None and self.rtype == 10:
            return f"AcMoment({limit_string(self.text_without_ubb, 7)} {self.linked})"
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

    @property
    def referer(self):
        return f"{routes['moment']}{self.am_num}"

    def up(self):
        user = self.raw_data.get('user')
        return self.acer.acfun.AcUp(user.get("id"))

    def comment(self):
        return self.acer.acfun.AcComment(self.resource_type, self.rid)

    def banana(self, count: int):
        return self.acer.throw_banana(self.rid, self.resource_type, count)


class MyMoment:
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

    @property
    def referer(self):
        rtypes = {
            "0": "?tab=all",
            "2": "?tab=video",
            "3": "?tab=article",
        }
        query = rtypes.get(str(self.resourceTypes), "")
        return f"{routes['feeds']}{query}"

    def set_tab(self, tab: str = 'all'):
        new = self.rts.get(tab, 0)
        if new != self.resourceTypes:
            self.resourceTypes = new
            self.cursor = "0"
            self.moment_data = list()
            return True
        return False

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
        return [AcMoment(self.acer, x) for x in api_data.get('feedList', [])]
