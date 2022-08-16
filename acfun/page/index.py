# coding=utf-8
import json
import os
import time
from bs4 import BeautifulSoup as Bs
from acfun.source import scheme, routes, apis, pagelets_from_page, pagelets_from_api
from acfun.page.utils import downloader, get_page_pagelets, AcPagelet

__author__ = 'dolacmeo'


class AcIndex:
    index_obj = None
    index_pagelets = []
    nav_data = dict()

    def __init__(self, acer=None):
        self.acer = acer
        self._get_index()

    def _get_index(self):
        req = self.acer.client.get(routes['index'])
        self.index_obj = Bs(req.text, 'lxml')
        self.index_pagelets = get_page_pagelets(self.index_obj)

    def _get_pagelet_inner(self, area: [str, None] = None):
        datas = dict()
        for js in self.index_obj.select("script"):
            if js.text.startswith("bigPipe.onPageletArrive"):
                data = json.loads(js.text[24:-2])
                datas[data['id']] = data
        datas['footer'] = self.index_obj.select_one('#footer')
        if isinstance(area, str):
            return datas.get(area)
        return datas

    def _get_pagelet_api(self, area):
        assert area in pagelets_from_api
        param = {
            "pagelets": area, "reqID": 0, "ajaxpipe": 1,
            "t": str(time.time_ns())[:13]
        }
        req = self.acer.client.get(routes['index'] + '/', params=param)
        if req.text.endswith("/*<!-- fetch-stream -->*/"):
            return json.loads(req.text[:-25])
        return req.json()

    def nav_list(self):
        navs = list()
        for cid in self.acer.nav_data.keys():
            navs.append(self.acer.AcChannel(cid))
        return navs

    def get(self, area: str, obj=False):
        if area != 'footer' and not area.startswith("pagelet_"):
            area = "pagelet_" + area
        if area in pagelets_from_page:
            raw_data = self._get_pagelet_inner(area)
        elif area in pagelets_from_api:
            raw_data = self._get_pagelet_api(area)
        else:
            raise ValueError('area not support')
        acp = AcPagelet(self.acer, raw_data)
        return acp.to_dict(obj)


class AcDownload:
    default_dest = os.path.join(os.getcwd(), 'download')

    def __init__(self, acer):
        self.acer = acer
        if os.path.exists(self.default_dest) is False:
            os.mkdir(self.default_dest)

    def emots(self, dest_path: [str, None] = None):
        dest_path = self.default_dest if dest_path is None else dest_path
        emot_page = self.acer.client.get(routes['emot'])
        emot_obj = Bs(emot_page.text, 'lxml')
        for item in emot_obj.select('.emot-download a.download-btn'):
            furl = f"{scheme}:{item.attrs['href']}"
            downloader(self.acer.client, furl, dest_dir=dest_path)
        return dest_path

    def Android_apk(self, dest_path: [str, None] = None):
        dest_path = self.default_dest if dest_path is None else dest_path
        api_req = self.acer.client.get(apis['app_download'])
        api_data = api_req.json()
        downloader(self.acer.client, api_data.get('url'), dest_dir=dest_path)
        return dest_path

    def _app_page_obj(self):
        page_req = self.acer.client.get(routes['app'])
        return Bs(page_req.text, 'lxml')

    def LiveMate_win(self, dest_path: [str, None] = None):
        dest_path = self.default_dest if dest_path is None else dest_path
        win_link = self._app_page_obj().select_one('.zbbl-info .download a.win')
        downloader(self.acer.client, win_link.attrs['href'], dest_dir=dest_path)
        return dest_path

    def VirtualView_win(self, dest_path: [str, None] = None):
        dest_path = self.default_dest if dest_path is None else dest_path
        win_link = self._app_page_obj().select_one('.mbzs-info .download a.win')
        downloader(self.acer.client, win_link.attrs['href'], dest_dir=dest_path)
        psd_link = self._app_page_obj().select_one('.mbzs-info .dis a.download-psd')
        downloader(self.acer.client, psd_link.attrs['href'], dest_dir=dest_path)
        return dest_path

