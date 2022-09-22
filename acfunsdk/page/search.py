# coding=utf-8
from .utils import json, time, parse, Bs
from .utils import AcSource

__author__ = 'dolacmeo'


class AcSearch:
    reqID = 0
    result_raw = None
    result_obj = None
    hot_keywords = dict()
    sort_type = ['相关', '最多观看', '最多评论', '最多收藏', '最新发布']
    search_types = {
        'complex': 'complex-list',
        'video': 'video-list',
        'user': 'user-list',
        'article': 'article-list',
        'bangumi': 'bangumi-list',
        'album': 'album-list',
    }

    def __init__(self, acer, keyword: [str, None] = None, s_type: [str, None] = None):
        self.acer = acer
        self._get_keywords()
        if keyword is None and 'searchKeywords' in self.hot_keywords:
            self.keyword = self.hot_keywords['searchKeywords'][0].get('keyword')
        else:
            self.keyword = keyword
        assert self.keyword
        if s_type in self.search_types:
            self.search_type = s_type
        else:
            self.search_type = 'complex'

    @property
    def referer(self):
        param = {
            "keyword": self.keyword,
            "type": self.search_type,
            "pCursor": 1,
        }
        return f"{AcSource.routes['search']}?{parse.urlencode(param)}"

    def _get_data(self, page: int = 1, sortby: int = 1, channel_id: int = 0):
        if 1 > sortby > 5:
            sortby = 1
        param = {
            "keyword": self.keyword,
            "type": self.search_type,
            "quickViewId": self.search_types[self.search_type],
            "reqID": self.reqID,
            "ajaxpipe": 1,
            "pCursor": page,
            "sortType": sortby,
            "channelId": channel_id,
            "t": str(time.time_ns())[:13],
        }
        api_req = self.acer.client.get(AcSource.apis['search'], params=param)
        assert api_req.text.endswith("/*<!-- fetch-stream -->*/")
        self.reqID += 1
        self.result_raw = json.loads(api_req.text[:-25])
        self.result_obj = Bs(self.result_raw.get('html', ''), 'lxml')

    def _get_keywords(self):
        api_req = self.acer.client.get(AcSource.apis['search_keywords'])
        api_data = api_req.json()
        if api_data.get('result') == 0:
            self.hot_keywords = api_data

    def page(self, num=1, sortby: int = 1, channel_id: int = 0) -> (list, None):
        self._get_data(num, sortby, channel_id)
        item_data = list()
        for item in self.result_obj.select('[class^=search-]'):
            if 'data-up-exposure-log' in item.attrs.keys():
                json_data = json.loads(item.attrs['data-up-exposure-log'])
                item_data.append(self.acer.acfun.AcUp(json_data['up_id']))
            else:
                json_data = json.loads(item.attrs['data-exposure-log'])
                if 'search-video' in item.attrs['class']:
                    item_data.append(self.acer.acfun.AcVideo(json_data['content_id'], {"title": json_data['title']}))
                elif 'search-article' in item.attrs['class']:
                    item_data.append(self.acer.acfun.AcArticle(json_data['content_id'], {"title": json_data['title']}))
                elif 'search-album' in item.attrs['class']:
                    item_data.append(self.acer.acfun.AcAlbum(json_data['content_id']))
                elif 'search-bangumi' in item.attrs['class']:
                    item_data.append(self.acer.acfun.AcBangumi(json_data['content_id']))
        return item_data




