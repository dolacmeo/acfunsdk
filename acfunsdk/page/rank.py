# coding=utf-8
from .utils import parse, Literal
from .utils import AcSource

__author__ = 'dolacmeo'


class AcRank:
    date_ranges = ['DAY', 'THREE_DAYS', 'WEEK']
    raw_data = None

    def __init__(self, acer,
                 cid: [int, None] = None,
                 sub_cid: [int, None] = None,
                 limit: int = 50,
                 date_range: Literal['DAY', 'THREE_DAYS', 'WEEK', None] = None):
        self.acer = acer
        self.cid = cid if isinstance(cid, int) else ""
        self.sub_cid = sub_cid if isinstance(sub_cid, int) else ""
        self.limit = limit
        self.date_range = date_range if date_range in self.date_ranges else self.date_ranges[0]
        self.get_data()

    def __repr__(self):
        this_id = self.sub_cid or self.cid or "ALL"
        return f"AcRank(#{this_id} {self.date_range})"

    @property
    def referer(self):
        param = {
            "pcid": self.cid or "-1",
            "cid": self.sub_cid or "-1",
            "range": self.date_range
        }
        return f"{AcSource.routes['rank']}?{parse.urlencode(param)}"

    def get_data(self):
        param = {
            "channelId": self.cid,
            "subChannelId": self.sub_cid,
            "rankLimit": self.limit,
            "rankPeriod": self.date_range
        }
        api_req = self.acer.client.get(AcSource.apis['rank_list'], params=param)
        if api_req.json().get('result') == 0:
            self.raw_data = api_req.json().get('rankList')

    def channel(self):
        return self.acer.acfun.AcChannel(self.sub_cid or self.cid)

    def contents(self) -> (list, None):
        if self.raw_data is None:
            return None
        data_list = list()
        for content in self.raw_data:
            if content['contentType'] == 2:
                data_list.append(self.acer.acfun.AcVideo(content['dougaId'], content))
            elif content['contentType'] == 3:
                data_list.append(self.acer.acfun.AcArticle(content['resourceId'], content))
        return data_list

    def ups(self) -> (list, None):
        if self.raw_data is None:
            return None
        data_list = list()
        for content in self.raw_data:
            data_list.append(self.acer.acfun.AcUp(content['userId']))
        return data_list
