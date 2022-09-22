# coding=utf-8
from .utils import json, math, time, parse, Bs, Literal
from .utils import AcSource, AcDetail, not_404, get_channel_info

__author__ = 'dolacmeo'


class AcBangumi(AcDetail):

    def __init__(self, acer, rid: [str, int]):
        if isinstance(rid, str) and rid.startswith('aa'):
            rid = rid[2:]
        if "_36188_" in rid:
            rid, _ = map(int, rid.split('_36188_'))
        super().__init__(acer, 1, rid)

    def loading_more(self):
        self.raw_data.update(get_channel_info(self.page_text))

    @not_404
    def video(self, index: int = 0):
        assert index in range(len(self.episode_data))
        vid = self.episode_data[index]
        ends = f"_36188_{vid['videoId']}" if index > 0 else ""
        title = "" if len(self.episode_data) == 1 else vid['episodeName']
        return self.get_video(vid['videoId'], title, f"{self.referer}{ends}")

    @property
    @not_404
    def bangumi_data(self):
        return self.raw_data.get("data")

    @property
    @not_404
    def bangumi_list(self):
        return self.raw_data.get("list")

    @property
    @not_404
    def season_data(self):
        return self.bangumi_data.get('relatedBangumis', [])

    @property
    @not_404
    def episode_data(self):
        return self.bangumi_list.get('items', [])

    @property
    def title(self):
        if self.is_404:
            return self._msg['404']
        return self.bangumi_data.get('bangumiTitle')

    @property
    def cover(self):
        if self.is_404:
            return None
        return self.cover_image()

    def cover_image(self, v_or_h: Literal["v", "h", "V", "H"] = "h"):
        return self.bangumi_data.get(f"bangumiCoverImage{v_or_h.upper()}")

    def __repr__(self):
        return f"AcBangumi([aa{self.resource_id}]{self.title})".encode(errors='replace').decode()


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
        return f"{AcSource.routes['bangumi_list']}"

    def loading(self):
        index_req = self.acer.client.get(AcSource.routes['bangumi_list'])
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
        page_req = self.acer.client.get(AcSource.routes['bangumi_list'], params=param)
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
