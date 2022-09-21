# coding=utf-8
from .utils import AcSource, AcDetail, not_404

__author__ = 'dolacmeo'


class AcAlbum(AcDetail):
    content_list = list()

    def __init__(self, acer, rid: [str, int]):
        if isinstance(rid, str) and rid.startswith('aa'):
            rid = rid[2:]
        self.acer = acer
        super().__init__(acer, 4, rid)

    @property
    def info(self):
        return self.raw_data.get("albumInfo", {})

    @property
    def title(self):
        if self.is_404:
            return self._msg['404']
        return self.info.get('title')

    @not_404
    def up_uid(self):
        return self.info.get("authorId")

    @not_404
    def up_name(self):
        return self.info.get("authorName")

    @not_404
    def up(self):
        return self.acer.acfun.AcUp(self.up_uid)

    def __repr__(self):
        if self.is_404:
            return f"AcAlbum([aa{self.resource_id}] 404)"
        return f"AcAlbum([aa{self.resource_id}]{self.title} @{self.up_name})".encode(errors='replace').decode()

    def loading_more(self):
        self._get_all_content()

    def _get_content(self, page: int = 1, limit: int = 50):
        param = {
            "page": page,
            "size": limit,
            "arubamuId": self.resource_id
        }
        api_req = self.acer.client.get(AcSource.apis['album_list'], params=param)
        return api_req.json()

    def _get_all_content(self):
        raw_contents = self.raw_data.get("albumContent", {})
        if len(raw_contents['contentList']) == raw_contents['totalSize']:
            self.content_list = raw_contents['contentList']
            return True
        self.content_list = list()
        page, page_max = 1, 2
        while page <= page_max:
            api_data = self._get_content(page)
            if api_data.get('result') != 0:
                break
            self.content_list.extend(api_data.get('contents', []))
            page_max = api_data.get('pageCount', page)
            page = api_data.get('page', 1)
            page += 1

    @not_404
    def list(self, obj: bool = False):
        if obj is False:
            return self.content_list
        if len(self.content_list) == 0:
            self._get_all_content()
        data_list = list()
        for content in self.content_list:
            if content['resourceTypeValue'] == 2:
                data_list.append(self.acer.acfun.AcVideo(content['resourceId']))
            elif content['resourceTypeValue'] == 3:
                data_list.append(self.acer.acfun.AcArticle(content['resourceId']))
        return data_list
