# coding=utf-8
import json
from bs4 import BeautifulSoup as Bs
from acfunsdk.source import routes, apis
from acfunsdk.page.utils import match1

__author__ = 'dolacmeo'


class AcAlbum:
    resource_type = 4
    aa_num = None
    page_obj = None
    page_data = None
    content_data = list()
    is_404 = False

    def __init__(self, acer, aa_num: [str, int]):
        self.acer = acer
        if isinstance(aa_num, str) and aa_num.startswith('aa'):
            aa_num = aa_num[2:]
        self.aa_num = str(aa_num)
        self.loading()

    @property
    def referer(self):
        return f"{routes['album']}{self.aa_num}"

    def __repr__(self):
        if self.is_404:
            return f"AcAlbum([aa{self.aa_num}] 404)"
        return f"AcAlbum([aa{self.aa_num}]{self.info['title']} @{self.info['authorName']})".encode(errors='replace').decode()

    def loading(self):
        req = self.acer.client.get(f"{routes['album']}{self.aa_num}")
        self.is_404 = req.status_code // 100 != 2
        if self.is_404:
            return None
        self.page_obj = Bs(req.text, 'lxml')
        json_text = match1(req.text, r"(?s)__INITIAL_STATE__\s*=\s*(\{.*?\});")
        self.page_data = json.loads(json_text)
        self._get_all_content()

    def up(self):
        return self.acer.acfun.AcUp(self.info.get("authorId"))

    @property
    def info(self):
        return self.page_data.get('album', {}).get('albumInfo', {})

    def _get_content(self, page: int = 1, limit: int = 50):
        param = {
            "page": page,
            "size": limit,
            "arubamuId": self.aa_num
        }
        api_req = self.acer.client.get(apis['album_list'], params=param)
        return api_req.json()

    def _get_all_content(self):
        self.content_data = list()
        page = 1
        page_max = 2
        while page <= page_max:
            api_data = self._get_content(page)
            if api_data.get('result') != 0:
                break
            self.content_data.extend(api_data.get('contents', []))
            page_max = api_data.get('pageCount', page)
            page = api_data.get('page', 1)
            page += 1

    def list(self):
        if len(self.content_data) == 0:
            self._get_all_content()
        data_list = list()
        for content in self.content_data:
            if content['resourceTypeValue'] == 2:
                data_list.append(self.acer.acfun.AcVideo(content['resourceId'], content))
            elif content['resourceTypeValue'] == 3:
                data_list.append(self.acer.acfun.AcArticle(content['resourceId'], content))
        return data_list

    def favorite_add(self):
        return self.acer.favourite.add(self.aa_num, 4)

    def favorite_cancel(self):
        return self.acer.favourite.cancel(self.aa_num, 4)

    def report(self, crime: str, proof: str, description: str):
        return self.acer.acfun.AcReport.submit(
            self.referer, self.aa_num, self.resource_type,
            self.info.get("authorId", "0"),
            crime, proof, description)
