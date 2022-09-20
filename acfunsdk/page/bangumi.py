# coding=utf-8
import time
import json
import math
from urllib import parse
from bs4 import BeautifulSoup as Bs
from acfunsdk.source import routes, apis
from acfunsdk.page.utils import get_channel_info, get_page_pagelets, match1

__author__ = 'dolacmeo'


class AcBangumi:
    resource_type = 1
    aa_num = None
    page_obj = None
    page_pagelets = []
    bangumi_data = None
    bangumi_list = None
    vid = None
    item_id = None
    resourceType = 6
    is_404 = False

    def __init__(self, acer, aa_num: [str, int]):
        if isinstance(aa_num, str) and aa_num.startswith('aa'):
            aa_num = aa_num[2:]
        self.aa_num = str(aa_num)
        self.acer = acer
        self.loading()
        if self.is_404 is False:
            self.set_video()

    def __repr__(self):
        if self.is_404:
            return f"AcBangumi([ac{self.aa_num}]咦？世界线变动了。看看其他内容吧~)"
        title = self.bangumi_data.get('showTitle', self.bangumi_data.get('bangumiTitle', ""))
        return f"AcBangumi([ac{self.aa_num}_{self.item_id}]{title})".encode(errors='replace').decode()

    @property
    def referer(self):
        if self.item_id is None:
            return f"{routes['bangumi']}{self.aa_num}"
        return f"{routes['bangumi']}{self.aa_num}_36188_{self.item_id}"

    def loading(self):
        req = self.acer.client.get(routes['bangumi'] + self.aa_num)
        self.is_404 = req.status_code // 100 != 2
        if self.is_404:
            return False
        self.page_obj = Bs(req.text, 'lxml')
        script_bangumidata, script_bangumilist = match1(req.text,
                                                        r"(?s)bangumiData\s*=\s*(\{.*?\});",
                                                        r"(?s)bangumiList\s*=\s*(\{.*?\});")
        self.bangumi_data = json.loads(script_bangumidata)
        self.bangumi_list = json.loads(script_bangumilist)
        self.bangumi_data.update(get_channel_info(req.text))
        self.item_id = self.bangumi_data.get("itemId")
        self.vid = self.bangumi_data.get("videoId")
        self.page_pagelets = get_page_pagelets(self.page_obj)

    @property
    def season_data(self):
        return self.bangumi_data.get('relatedBangumis', [])

    @property
    def episode_data(self):
        return self.bangumi_list.get('items', [])

    def set_video(self, num=1):
        if num > len(self.episode_data):
            return False
        this_episode = self.episode_data[num - 1]
        self.vid = this_episode['videoId']
        self.item_id = this_episode['itemId']
        self.bangumi_data.update({
            'videoId': self.vid, 'itemId': self.item_id,
            'showTitle': f"{this_episode['bangumiTitle']} {this_episode['episodeName']} {this_episode['title']}"
        })
        return True

    def danmaku(self):
        return self.acer.acfun.AcDanmaku(self.bangumi_data)

    def comment(self):
        return self.acer.acfun.AcComment(f"{self.aa_num}_{self.vid}", 6)

    def like(self):
        return self.acer.like_add(self.item_id, 18)

    def like_cancel(self):
        return self.acer.like_delete(self.item_id, 18)

    def favorite_add(self):
        return self.acer.favourite.add(self.aa_num, 1)

    def favorite_cancel(self):
        return self.acer.favourite.cancel(self.aa_num, 1)

    def banana(self):
        return self.acer.throw_banana(self.item_id, 18, 1)

    def report(self, crime: str, proof: str, description: str):
        return self.acer.acfun.AcReport.submit(
            self.referer, self.aa_num, self.resource_type, "0",
            crime, proof, description)


class AcBangumiList:
    page_obj = None
    menu_filter = list()
    default_filter = None

    def __init__(self, acer):
        self.acer = acer
        self.loading()

    def __repr__(self):
        return f"AcBangumiList(番剧列表 - AcFun弹幕视频网)"

    @property
    def referer(self):
        return f"{routes['bangumi_list']}"

    def loading(self):
        index_req = self.acer.client.get(routes['bangumi_list'])
        self.page_obj = Bs(index_req.text, 'lxml')
        firsts = []
        for menu in self.page_obj.select(".ac-menu .ac-menu-filter"):
            menu_id = int(menu.attrs['data-id'])
            filter_title = menu.select_one('.ac-menu-filter-title').text.replace(":", "")
            filter_item = {item.attrs['data-id']: item.text for item in menu.select(".ac-menu-filter-item")}
            self.menu_filter.append({'title': filter_title, 'item': filter_item, 'menu_id': menu_id})
            default_id = menu.select_one(".ac-menu-filter-item").attrs['data-id']
            firsts.append([menu_id, default_id])
        self.menu_filter = sorted(self.menu_filter, key=lambda m: m['menu_id'])
        firsts = sorted(firsts, key=lambda i: i[0])
        self.default_filter = ",".join([n[1] for n in firsts])

    def _filter_check(self, filters: [str, list]):
        filters = filters.split(",") if isinstance(filters, str) else filters
        if len(filters) != len(self.menu_filter):
            return False
        for n in range(len(filters)):
            if filters[n] not in self.menu_filter[n]['item']:
                print(f"{filters[n]} not in {self.menu_filter[n]['title']}: {self.menu_filter[n]['item'].keys()}")
                return False
        return True

    def tans_filters(self, words: [str, list]):
        filters = words.split(",") if isinstance(words, str) else words
        if len(filters) != len(self.menu_filter):
            return False
        v = list()
        for n in range(len(filters)):
            if filters[n] not in self.menu_filter[n]['item'].values():
                return False
            _inverse = {v: k for k, v in self.menu_filter[n]['item'].items()}
            v.append(_inverse[filters[n]])
        return ",".join(v)

    def page_from_url(self, full_url: str, obj: bool = False):
        filters = self.default_filter
        page = 1
        param = parse.urlsplit(full_url).query
        param = parse.parse_qs(param)
        if "filters" in param:
            filters = param['filters'][0]
        if "pageNum" in param:
            page = int(param['pageNum'][0])
        return self.page(filters, page, obj)

    def page(self, filters: [str, list, None] = None, page: int = 1, obj: bool = False):
        filters = self.default_filter if filters is None else filters
        if self._filter_check(filters) is False:
            return None
        filters = ",".join(filters) if isinstance(filters, list) else filters
        param = {
            "quickViewId": "bangumiList",
            "filters": filters,
            "reqID": 1, "ajaxpipe": 1,
            "pageNum": page,
            "t": str(time.time_ns())[:13]
        }
        page_req = self.acer.client.get(routes['bangumi_list'], params=param)
        if not page_req.text.endswith("/*<!-- fetch-stream -->*/"):
            return None
        api_data = json.loads(page_req.text[:-25])
        page_obj = Bs(api_data.get('html', ''), 'lxml')
        ac_list = page_obj.select_one(".ac-mod-list")
        item_total = int(ac_list.attrs['data-totalcount'])
        page_size = int(ac_list.attrs['data-pagesize'])
        max_page = math.ceil(item_total / page_size)
        items = list()
        for item in ac_list.select("li.ac-mod-li"):
            item_data = {
                "aa_num": item.attrs['data-aid'],
                "link": item.select_one('.ac-mod-link').attrs['href'],
                "cover": item.select_one('img.ac-mod-cover').attrs['src'],
                "cover_stats": item.select_one('.ac-mod-cover-stats').text,
                "need_pay": item.select_one('.pay-toast') is not None,
                "title": item.select_one('.ac-mod-title').text,
                "latestItem": item.select_one('.ac-mod-title > em').text,
            }
            if obj is True:
                items.append(AcBangumi(self.acer, item_data['aa_num']))
            else:
                items.append(item_data)
        return {
            "items": items,
            "page_now": page,
            "page_total": max_page,
            "page_size": page_size,
            "total_count": item_total
        }

    pass
