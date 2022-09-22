# coding=utf-8
from .utils import AcSource, AcDetail, resource_type_str_map, thin_string, limit_string

__author__ = 'dolacmeo'


class AcMoment(AcDetail):

    def __init__(self, acer, rid: [str, int]):
        if isinstance(rid, str) and rid.startswith('am'):
            rid = rid[2:]
        self.acer = acer
        super().__init__(acer, 10, rid)

    def loading_more(self):
        self.raw_data = self.raw_data.get("moment", {})

    @property
    def title(self):
        if self.is_404:
            return self._msg['404']
        text = self.raw_data.get("replaceUbbText", "")
        return thin_string(text)

    @property
    def moment_data(self):
        return self.raw_data.get('moment')

    @property
    def source_data(self):
        return self.raw_data.get('repostSource')

    @property
    def source_obj(self):
        if not isinstance(self.source_data, dict):
            return None
        return self.acer.acfun.resource(self.source_data['resourceType'], self.source_data['resourceId'])

    @property
    def source_describe(self):
        if not isinstance(self.source_data, dict):
            return None
        rtype = resource_type_str_map[str(self.source_data['resourceType'])]
        rid = self.source_data['resourceId']
        content = limit_string(self.source_data.get("discoveryResourceFeedShowContent", ""), 10)
        content = ("#" + content) if len(content) else ""
        up_data = self.source_data['user']
        up_name = up_data['userName']
        return f"⋙{rtype}@{up_name}{content}"

    def __repr__(self):
        up_data = self.moment_data['user']
        up_name = up_data['name']
        txt_show = limit_string(self.title, 10)
        with_img = f"∮图x{len(self.moment_data['imgs'])}" if 'imgs' in self.moment_data else ""
        return f"AcMoment(@{up_name}#{txt_show}{with_img}{self.source_describe or ''})"


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
        return f"{AcSource.routes['feeds']}{query}"

    def set_tab(self, tab: str = 'all') -> bool:
        new = self.rts.get(tab, 0)
        if new != self.resourceTypes:
            self.resourceTypes = new
            self.cursor = "0"
            self.moment_data = list()
            return True
        return False

    def feed(self, limit: int = 10, obj: bool = False, refresh: bool = False) -> (dict, None):
        if refresh is True:
            self.cursor = "0"
            self.moment_data = list()
        param = {
            "useWebp": False,
            "pcursor": self.cursor,
            "count": limit or self.limit,
            "resourceTypes": self.resourceTypes,
        }
        api_req = self.acer.client.get(AcSource.apis['follow_feed'], params=param)
        api_data = api_req.json()
        if api_data.get('result') == 0:
            self.cursor = api_data.get('pcursor', self.cursor)
            self.moment_data.extend(api_data.get('feedList', []))
        if obj is False:
            return api_data.get('feedList', [])
        result = list()
        for x in api_data.get('feedList', []):
            result.append(self.acer.acfun.resource(x['resourceType'], x['resourceId']))
        return result
