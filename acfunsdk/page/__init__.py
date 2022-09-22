# coding=utf-8
import re
import httpx
from urllib import parse
from ..source import AcSource
from .index import AcIndex
from .channel import AcChannel
from .rank import AcRank
from .search import AcSearch
from .member import AcUp
from .article import AcArticle, AcWen
from .bangumi import AcBangumi, AcBangumiList
from .video import AcVideo
from .album import AcAlbum
from .moment import AcMoment, MyMoment
from .live import AcLive, AcLiveUp
from .doodle import AcDoodle
from .comment import AcComment
from .danmaku import AcDanmaku
from .message import MyMessage
from .acer import MyFansClub, MyFollow, MyFavourite, MyAlbum, MyContribute, MyDanmaku, BananaMall
from .extra import AcLink, AcImage, AcHelp, AcInfo, AcAcademy, AcReport, AcDownload, AcLab, AcScreeningRoom
from .utils import B64s, match1, get_page_pagelets, resource_type_map, routes_type_map

__author__ = 'dolacmeo'


class AcFun:
    nav_data = dict()
    channel_data = AcSource.channel_data
    AcInfo = AcInfo
    AcReport = AcReport
    AcAcademy = AcAcademy
    AcHelp = AcHelp
    AcLab = AcLab

    def __init__(self, acer):
        self.acer = acer
        self.cdn_domain = self.acer.client.post(AcSource.apis['cdn_domain'], headers={
            "referer": AcSource.routes['index']}).json().get('domain')
        self._get_nav()

    def _get_nav(self):
        data = self.acer.client.get(AcSource.apis['nav']).json().get("data", [])
        for i in data:
            if i['cid'] != 0:
                self.nav_data.update({str(i['cid']): {x: i[x] for x in i if x != 'children'}})
            for j in i['children']:
                if j['cid'] != 0:
                    self.nav_data.update({str(j['cid']): {y: j[y] for y in j if y != 'children'}})

    @property
    def referer(self) -> str:
        return f"{AcSource.routes['index']}"

    def search_user(self, keyword: str, page: int = 1, obj: bool = False) -> dict:
        api_req = self.acer.client.get(AcSource.apis['search_user'], params={'keyword': keyword, "pCursor": page})
        api_data = api_req.json()
        if obj is False:
            return api_data
        objs = list()
        for x in api_data.get("userList", []):
            objs.append(self.AcUp(x['id']))
        api_data["userList"] = objs
        return api_data

    def username_check(self, name: str) -> bool:
        api_req = self.acer.client.post(AcSource.apis['check_username'], data={'name': name})
        api_data = api_req.json()
        if api_data.get('result') == 0:
            return True
        print(api_data['error_msg'])
        return False

    def AcIndex(self) -> object:
        return AcIndex(self.acer)

    def AcChannel(self, cid) -> object:
        return AcChannel(self.acer, cid)

    def AcBangumiList(self) -> object:
        return AcBangumiList(self.acer)

    def AcWen(self,
              realm_ids: [list, None] = None,
              sort_type: str = "createTime",
              time_range: str = "all",
              only_original: bool = False,
              limit: int = 10) -> object:
        return AcWen(self.acer, realm_ids, sort_type, time_range, only_original, limit)

    def AcRank(self,
               cid: [int, None] = None,
               sub_cid: [int, None] = None,
               limit: int = 50,
               date_range: [str, None] = None) -> object:
        return AcRank(self.acer, cid, sub_cid, limit, date_range)

    def AcSearch(self, keyword: [str, None] = None, s_type: [str, None] = None) -> object:
        return AcSearch(self.acer, keyword, s_type)

    def AcUp(self, uid) -> object:
        return AcUp(self.acer, uid)

    def AcLiveUp(self, uid) -> object:
        return AcLiveUp(self.acer, uid)

    def AcArticle(self, ac_num) -> object:
        return AcArticle(self.acer, ac_num)

    def AcVideo(self, ac_num) -> object:
        return AcVideo(self.acer, ac_num)

    def AcBangumi(self, aa_num) -> object:
        return AcBangumi(self.acer, aa_num)

    def AcAlbum(self, ac_num) -> object:
        return AcAlbum(self.acer, ac_num)

    def AcLive(self) -> object:
        return AcLive(self.acer)

    def AcDoodle(self, doodle_id: str) -> object:
        return AcDoodle(self.acer, doodle_id)

    def AcMoment(self, am_num) -> object:
        return AcMoment(self.acer, am_num)

    def AcDownload(self) -> object:
        return AcDownload(self.acer)

    def AcScreeningRoom(self) -> object:
        return AcScreeningRoom(self.acer)

    def AcComment(self, rtype: int, rid: int) -> object:
        return AcComment(self.acer, rtype, rid)

    def AcDanmaku(self, video_id: int, parent) -> object:
        return AcDanmaku(self.acer, video_id, parent)

    def AcImage(self, src, url=None, name=None) -> object:
        return AcImage(self.acer, src, url, name)

    def AcLink(self, url, title=None) -> object:
        return AcLink(self.acer, url, title)

    def resource(self, rtype: int, rid: int) -> object:
        assert str(rtype) in resource_type_map.keys()
        return getattr(self, resource_type_map[str(rtype)])(rid)

    def get(self, url_str: str, title=None) -> (object, None):
        if url_str.startswith("http://"):
            url_str = url_str.replace("http://", "https://")
        if url_str in [AcSource.routes['index'], AcSource.routes['index'] + "/"]:
            return self.AcIndex()
        elif url_str in [AcSource.routes['live_index'], AcSource.routes['live_index'] + "/"]:
            return self.AcLive()
        for link_name in routes_type_map.keys():
            if url_str.startswith(AcSource.routes[link_name]):
                ends = url_str[len(AcSource.routes[link_name]):]
                return getattr(self, routes_type_map[link_name])(ends)
        for link_name in ['rank', 'bangumi_list']:
            if url_str.startswith(AcSource.routes[link_name]):
                ends = url_str[len(AcSource.routes[link_name]):]
                if link_name == 'bangumi_list':
                    return self.AcBangumiList()
                elif link_name == 'rank':
                    q = parse.parse_qs(parse.urlsplit(url_str).query)
                    kw = {
                        'cid': None if q.get('pcid', "-1") == "-1" else int(q['pcid'][0]),
                        'sub_cid': None if q.get('cid', "-1") == "-1" else int(q['cid'][0]),
                        'date_range': q.get("range", ['DAY'])[0],
                    }
                    return self.AcRank(**kw)
                return getattr(self, f"Ac{link_name.capitalize()}")(ends)
        channel_rex = re.compile(rf"^{AcSource.routes['index']}/v/list(\d+)/index.htm").findall(url_str)
        if channel_rex:
            return self.AcChannel(channel_rex[0])
        if "//hd.acfun.cn/s/" in url_str:
            req3xx = httpx.get(url_str)
            req_redirect = parse.urlsplit(req3xx.headers.get("Location", ""))
            w_link = parse.parse_qs(req_redirect.query).get("wLink", [])
            if len(w_link):
                return self.get(w_link[0])
        if url_str.startswith('http') and parse.urlsplit(url_str).netloc.endswith('acfun.cn'):
            if parse.urlsplit(url_str).netloc in self.cdn_domain:
                return AcImage(self.acer, url_str)
            return AcLink(self.acer, url_str, title)
        return None
