# coding=utf-8
import json
import time
from bs4 import BeautifulSoup as Bs
from acfun.source import routes, apis

__author__ = 'dolacmeo'


class AcUp:
    uid = None
    up_data = None
    up_page = None

    video_count = None
    article_count = None
    album_count = None
    following_count = None
    followed_count = None

    def __init__(self, acer, up_data: dict):
        self.up_data = up_data
        self.uid = str(self.up_data.get('userId', str(self.up_data.get('id', ''))))
        self.acer = acer
        self._get_acup()

    def _get_acup(self):
        api_req = self.acer.client.get(apis['userInfo'], params={"userId": self.uid})
        if api_req.json().get('result') == 0:
            self.up_data.update(api_req.json().get('profile', {}))

    @property
    def name(self):
        return self.up_data.get('userName', self.up_data.get('name'))

    def __repr__(self):
        return f"Acer([{self.uid}] @{self.name})".encode(errors='replace').decode()

    def loading(self):
        page_req = self.acer.client.get(routes['up'] + self.uid)
        self.up_page = Bs(page_req.text, "lxml")
        self.video_count = self.up_page.select_one(
            '.ac-space-contribute-list > .tags > li[data-index=video]').attrs['data-count']
        self.article_count = self.up_page.select_one(
            '.ac-space-contribute-list > .tags > li[data-index=article]').attrs['data-count']
        self.album_count = self.up_page.select_one(
            '.ac-space-contribute-list > .tags > li[data-index=album]').attrs['data-count']
        self.following_count = self.up_page.select_one(
            '.tab-list > li[data-index=following] > span').text
        self.followed_count = self.up_page.select_one(
            '.tab-list > li[data-index=followed] > span').text

    def AcLive(self):
        return self.acer.AcLiveUp(self.uid)

    def follow_add(self, attention: [bool, None] = None):
        return self.acer.follow_add(self.uid, attention)

    def follow_remove(self):
        return self.acer.follow_remove(self.uid)

    def _get_data(self, viewer, page, limit, orderby):
        viewers = ['video', 'article', 'album', 'following', 'followed']
        assert viewer in viewers
        orders = ['newest', 'hotest']
        assert orderby in orders
        param = {
            "reqID": viewers.index(viewer) + 1,
            "ajaxpipe": 1,
            "type": viewer,
            "page": page,
            "pageSize": limit,
            "t": str(time.time_ns())[:13]
        }
        if viewers.index(viewer) < 3:
            param.update({"quickViewId": f"ac-space-{viewer}-list", "order": orderby})
        else:
            param.update({"quickViewId": f"ac-space-{viewer}-user-list"})
        req = self.acer.client.get(routes['up'] + self.uid, params=param)
        assert req.text.endswith("/*<!-- fetch-stream -->*/")
        return json.loads(req.text[:-25])

    def video(self, page=1, limit=10, orderby='newest'):
        data = list()
        acer_data = self._get_data('video', page, limit, orderby)
        for item in Bs(acer_data.get('html', ''), 'lxml').select('a.ac-space-video'):
            ac_num = item.attrs['href'][5:]
            infos = {
                'title': item.select_one('p.title').attrs['title'],
                'dougaId': ac_num,
                'coverUrl': item.select_one('.video > img').attrs['src'],
                'createTime': item.select_one('p.date').text.replace('/', '-'),
                'user': self.up_data
            }
            data.append(self.acer.AcVideo(ac_num, infos))
        return data

    def article(self, page=1, limit=10, orderby='newest'):
        data = list()
        acer_data = self._get_data('article', page, limit, orderby)
        for item in Bs(acer_data.get('html', ''), 'lxml').select('.ac-space-article'):
            ac_num = item.a.attrs['href'][5:]
            infos = {
                'title': item.a.attrs['title'],
                'dougaId': ac_num,
                'user': self.up_data
            }
            data.append(self.acer.AcArticle(ac_num, infos))
        return data

    def album(self, page=1, limit=10, orderby='newest'):
        data = list()
        acer_data = self._get_data('album', page, limit, orderby)
        for item in Bs(acer_data.get('html', ''), 'lxml').select('.ac-space-album'):
            ac_num = item.a.attrs['href'][5:]
            data.append(self.acer.AcAlbum(ac_num))
        return data

    def following(self, page=1, limit=10, orderby='newest'):
        data = list()
        acer_data = self._get_data('following', page, limit, orderby)
        for item in Bs(acer_data.get('html', ''), 'lxml').select('li'):
            infos = {
                "id": item.select_one('div:nth-of-type(2) > a.name').attrs['href'][3:],
                "name": item.select_one('div:nth-of-type(2) > a.name').text
            }
            data.append(self.acer.AcUp(infos))
        return data

    def followed(self, page=1, limit=10, orderby='newest'):
        data = list()
        acer_data = self._get_data('followed', page, limit, orderby)
        for item in Bs(acer_data.get('html', ''), 'lxml').select('li'):
            infos = {
                "id": item.select_one('div:nth-of-type(2) > a.name').attrs['href'][3:],
                "name": item.select_one('div:nth-of-type(2) > a.name').text
            }
            data.append(self.acer.AcUp(infos))
        return data
