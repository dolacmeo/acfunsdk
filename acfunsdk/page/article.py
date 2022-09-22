# coding=utf-8
from .utils import AcSource, AcDetail, not_404

__author__ = 'dolacmeo'


class AcArticle(AcDetail):

    def __init__(self, acer, rid: [str, int]):
        if isinstance(rid, str) and rid.startswith('ac'):
            rid = rid[2:]
        super().__init__(acer, 3, rid)

    @property
    def title(self):
        if self.is_404:
            return self._msg['404']
        return self.raw_data.get('contentTitle', self.raw_data.get('title', ""))

    @property
    def cover(self):
        if self.is_404:
            return None
        return self.raw_data.get("coverUrl")

    def __repr__(self):
        user_name = self._up_name or self._up_uid
        user_txt = "" if len(user_name) == 0 else f" @{user_name}"
        return f"AcArticle([ac{self.resource_id}]{self.title}{user_txt})".encode(errors='replace').decode()

    @not_404
    def recommends(self, obj: bool = False) -> (dict, None):
        articles = list()
        for item in self.page_obj.select('#main > section.area > .content > .fr > .contribution.weblog-item'):
            this_url = item.select_one('.contb-title a').attrs['href']
            ac_num = this_url[5:]
            data = {
                'title': item.select_one('.contb-title').a.text,
                'shareUrl': AcSource.routes['share'] + ac_num,
                'viewCount': item.select_one('.contb-count .view-count span.count').text,
                'commentCount': item.select_one('.contb-count .comm-count span.count').text,
                'user': self.raw_data.get('user', {})
            }
            if obj is True:
                articles.append(AcArticle(self.acer, ac_num))
            else:
                articles.append(data)
        return articles

    def AcWen(self) -> (object, None):
        if self.is_404:
            return None
        rid = self.raw_data.get("realm", {}).get("realmId")
        return AcWen(self.acer, [rid])

    def AcChannel(self) -> (object, None):
        if self.is_404:
            return None
        cid = self.raw_data.get("channel", {}).get('id')
        return self.acer.acfun.AcChannel(cid)


class AcWen:
    realmIds = None
    cursor = "first_page"
    sortType = "createTime"
    onlyOriginal = False
    timeRange = "all"
    limit = 10
    article_data = list()

    def __init__(self, acer,
                 realmIds: [list, None] = None,
                 sortType: str = "createTime",
                 timeRange: str = "all",
                 onlyOriginal: bool = False,
                 limit: int = 10):
        self.acer = acer
        self.realmIds = realmIds
        assert sortType in ['createTime', 'lastCommentTime', 'hotScore']
        self.sortType = sortType
        assert timeRange in ['all', 'oneDay', 'threeDay', 'oneWeek', 'oneMonth']
        self.timeRange = timeRange
        self.onlyOriginal = onlyOriginal
        self.limit = limit

    @property
    def referer(self):
        return f"{AcSource.routes['index']}/v/list63/index.htm"

    def feed(self, obj: bool = True) -> (dict, None):
        if self.cursor == 'no_more':
            return None
        form_data = {
            "cursor": self.cursor,
            "sortType": self.sortType,
            "onlyOriginal": self.onlyOriginal,
            "timeRange": self.timeRange,
            "limit": self.limit,
        }
        if isinstance(self.realmIds, list):
            form_data['realmId'] = self.realmIds
        api_req = self.acer.client.post(AcSource.apis['article_feed'], data=form_data)
        api_data = api_req.json()
        if api_data.get('result') == 0:
            self.cursor = api_data.get('cursor')
            new_data = api_data.get('data', [])
            self.article_data.extend(new_data)
            if obj is True:
                return [AcArticle(self.acer, x['articleId'], x) for x in new_data]
            return new_data
        return None

    def clean_cache(self) -> bool:
        self.article_data = list()
        return True
