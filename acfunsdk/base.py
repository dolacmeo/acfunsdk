# coding=utf-8
import os
import re
import json
import httpx
import datetime
from urllib import parse
from . import source
from .page import *
from .exceptions import *
from .saver import AcSaver

__author__ = 'dolacmeo'


class AcClient:
    _client = None
    history = list()

    def __init__(self, header=None):
        self._client = httpx.Client(headers=header or source.header)

    @property
    def cookies(self):
        return self._client.cookies

    @property
    def stream(self):
        return self._client.stream

    def request(self, *args, **kwargs):
        return self._client.request(*args, **kwargs)

    def get(self, *args, **kwargs):
        url = kwargs.get('url', args[0])
        self.history.append(['GET', url, datetime.datetime.now()])
        return self._client.get(*args, **kwargs)

    def post(self, *args, **kwargs):
        url = kwargs.get('url', args[0])
        self.history.append(['POST', url, datetime.datetime.now()])
        return self._client.post(*args, **kwargs)

    def put(self, *args, **kwargs):
        url = kwargs.get('url', args[0])
        self.history.append(['PUT', url, datetime.datetime.now()])
        return self._client.put(*args, **kwargs)

    def patch(self, *args, **kwargs):
        url = kwargs.get('url', args[0])
        self.history.append(['PATCH', url, datetime.datetime.now()])
        return self._client.put(*args, **kwargs)

    def delete(self, *args, **kwargs):
        url = kwargs.get('url', args[0])
        self.history.append(['DELETE', url, datetime.datetime.now()])
        return self._client.put(*args, **kwargs)


class Acer:
    debug = False
    client = None
    req_count = 0
    BASE_PATH = os.getcwd()
    DOWNLOAD_PATH = None

    did = None
    uid = None
    username = None
    is_logined = False
    cookie = None
    personal = dict()
    tokens = dict()
    nav_data = dict()
    channel_data = source.ChannelList

    message = None
    moment = None
    favourite = None

    ac_index = AcIndex
    ac_channel = AcChannel
    ac_wen = AcWen
    ac_rank = AcRank
    ac_search = AcSearch
    ac_up = AcUp
    ac_article = AcArticle
    ac_video = AcVideo
    ac_bangumi = AcBangumi
    ac_album = AcAlbum
    ac_comment = AcComment
    ac_link = AcLink
    ac_image = AcImage

    def __init__(self, debug: bool = False):
        self.debug = debug
        self.client = AcClient() if debug else httpx.Client(headers=source.header)
        self.moment = AcMoment(self)
        self._get_nav()
        self.cdn_domain = self.client.post(source.apis['cdn_domain'], headers={
            "referer": source.routes['index']}).json().get('domain')
        if self.check_online() is False:
            raise AcExploded("阿禅爆炸 (今天A站挂了吗？)")
        self._get_personal()

    def __repr__(self):
        show_name = self.username or ''
        return f"Acer(#{self.uid or 'UNKNOWN'} {show_name})"

    def AcIndex(self):
        return AcIndex(self)

    def AcDownload(self):
        return AcDownload(self)

    def AcChannel(self, cid):
        return AcChannel(self, cid, self.nav_data.get(int(cid)))

    def AcWen(self,
              realmIds: [list, None] = None,
              sortType: str = "createTime",
              timeRange: str = "all",
              onlyOriginal: bool = False,
              limit: int = 10):
        return AcWen(self, realmIds, sortType, timeRange, onlyOriginal, limit)

    def AcRank(self,
               cid: [int, None] = None,
               sub_cid: [int, None] = None,
               limit: int = 50,
               date_range: [str, None] = None):
        return AcRank(self, cid, sub_cid, limit, date_range)

    def AcSearch(self, keyword: [str, None] = None, s_type: [str, None] = None):
        return AcSearch(self, keyword, s_type)

    def AcUp(self, updata):
        return AcUp(self, updata)

    def AcLiveUp(self, uid: int, raw=None):
        return AcLiveUp(self, uid, raw)

    def AcArticle(self, ac_num, data=None):
        return AcArticle(self, ac_num, data)

    def AcVideo(self, ac_num, data=None):
        return AcVideo(self, ac_num, data)

    def AcBangumi(self, aa_num):
        return AcBangumi(self, aa_num)

    def AcComment(self, ac_num, sourceType: int, referer: [str, None] = None):
        return AcComment(self, ac_num, sourceType, referer)

    def AcAlbum(self, ac_num):
        return AcAlbum(self, ac_num)

    def AcLive(self):
        return AcLive(self)

    def AcLink(self, url, title, container=None):
        return AcLink(self, url, title, container)

    def AcImage(self, src, url=None, name=None, container=None):
        return AcImage(self, src, url, name, container)

    def AcSaver(self, dest_path: [str, None] = None):
        return AcSaver(self, None, dest_path)

    def get(self, url_str: str, title=None):
        for link_name in ['video', 'article', 'album', 'bangumi', 'up', 'moment', 'live', 'share']:
            if url_str.startswith(source.routes[link_name]):
                ends = url_str[len(source.routes[link_name]):]
                if link_name == 'up':
                    return self.AcUp({'userId': ends})
                elif link_name == 'moment':
                    return self.moment.get(ends)
                elif link_name == 'share':
                    return self.AcVideo(ends)
                elif link_name == 'live':
                    return self.AcLiveUp(int(ends))
                return getattr(self, f"Ac{link_name.capitalize()}")(ends)
        channel_rex = re.compile(f"^{source.routes['index']}/v/list(\d+)/index.htm$").findall(url_str)
        if channel_rex:
            return self.AcChannel(channel_rex[0])
        if url_str.startswith('http') and parse.urlsplit(url_str).netloc.endswith('acfun.cn'):
            if parse.urlsplit(url_str).netloc in self.cdn_domain:
                return self.AcImage(url_str)
            return self.AcLink(url_str, title)
        return None

    def download(self, src_url, fname: [str, None] = None, dest_dir: [str, None] = None, display: bool = True):
        return downloader(self.client, src_url, fname, dest_dir, display)

    def check_online(self):
        req = self.client.get(source.routes['ico'], timeout=10)
        return req.status_code == 200

    def _get_nav(self):
        data = self.client.get(source.apis['nav']).json().get("data", [])
        for i in data:
            if i['cid'] != 0:
                self.nav_data.update({str(i['cid']): {x: i[x] for x in i if x != 'children'}})
            for j in i['children']:
                if j['cid'] != 0:
                    self.nav_data.update({str(j['cid']): {y: j[y] for y in j if y != 'children'}})

    def _get_personal(self):
        live_page_req = self.client.get(source.routes['live_index'])
        assert live_page_req.status_code // 100 == 2
        self.did = live_page_req.cookies.get('_did')
        if self.is_logined:
            api_req = self.client.post(source.apis['token'], data={"sid": "acfun.midground.api"})
            api_data = api_req.json()
            assert api_data.get('result') == 0
            self.tokens = {
                "ssecurity": api_data.get("ssecurity", ''),
                "api_st": api_data.get("acfun.midground.api_st", ''),
                "api_at": api_data.get("acfun.midground.api.at", ''),
            }
            info_req = self.client.get(source.apis['personalInfo'])
            info_data = info_req.json()
            assert info_data.get('result') == 0
            self.personal = info_data.get('info', {})
            self.uid = self.personal.get('userId')
            self.username = self.personal.get('userName')
            self.message = AcMessage(self)
            self.favourite = MyFavourite(self)
        else:
            api_req = self.client.post(source.apis['token_visitor'], data={"sid": "acfun.api.visitor"})
            api_data = api_req.json()
            assert api_data.get('result') == 0
            self.tokens = {
                "ssecurity": api_data.get("acSecurity", ''),
                "visitor_st": api_data.get("acfun.api.visitor_st", ''),
            }
            self.uid = api_data.get("userId")

    def update_token(self, data: dict):
        if self.is_logined:
            data.update({"acfun.midground.api_st": self.tokens['api_st']})
        else:
            data.update({"acfun.api.visitor_st": self.tokens['visitor_st']})
        return data

    def keys(self):
        return self.personal.keys()

    def loading(self, username):
        cookie_data = open(f'{username}.cookies', 'rb').read()
        cookie = B64s(cookie_data, len(username)).b64decode()
        self.cookie = json.loads(cookie.decode())
        self.client.cookies.update(self.cookie)
        self.is_logined = True
        self._get_personal()

    def login(self, username, password, key=None, captcha=None):
        form_data = {
            "username": username,
            "password": password,
            "key": key or "",
            "captcha": captcha or ""
        }
        api_req = self.client.post(source.apis['login'], data=form_data)
        result = api_req.json()
        self.is_logined = result.get('result', 1) == 0
        if self.is_logined is True:
            self._get_personal()
            cookie = json.dumps(dict(self.client.cookies.items()), separators=(',', ':'))
            cookie = B64s(cookie.encode(), len(username)).b64encode()
            with open(f'{username}.cookies', 'wb') as f:
                f.write(cookie)
        else:
            print(result)
            raise NotInCar('登录没成功，你到底是什么搞错了啊！')
        return self.is_logined

    def logout(self):
        self.client.get(source.apis['logout'])
        self.client = httpx.Client(headers=source.header)
        self.is_logined = False
        self.personal = dict()
        return True

    @need_login
    def update_signature(self, text: str):
        api_req = self.client.post(source.apis['updateSignature'], data={'signature': text},
                                   headers={'referer': 'https://www.acfun.cn/member/setting?tab=info'})
        return api_req.json().get('result') == 0

    @need_login
    def signin(self):
        api_req = self.client.get(source.apis['signIn'])
        api_data = api_req.json()
        print(api_data.get('msg'))
        return api_data.get('result') == 0

    @need_login
    def acoin(self):
        req = self.client.get(source.apis['acoinBalance'])
        data = req.json()
        if data.get('result') == 0:
            return data.get('data')
        return None

    def search_user(self, keyword: str):
        api_req = self.client.get(source.apis['search_user'], params={'keyword': keyword})
        return api_req.json()

    def username_check(self, name: str):
        api_req = self.client.post(source.apis['check_username'], data={'name': name})
        api_data = api_req.json()
        if api_data.get('result') == 0:
            return True
        print(api_data)
        return False

    @need_login
    def like(self, obj_id: str, objectType: int):
        form_data = {
            "kpn": "ACFUN_APP",
            "kpf": "PC_WEB",
            "subBiz": "mainApp",
            "interactType": 1,
            "objectType": objectType,
            "objectId": obj_id,
            "userId": self.uid,
        }
        form_data = self.update_token(form_data)
        req = self.client.post(source.apis['like_add'], data=form_data)
        return req.json().get('result') == 1

    @need_login
    def like_cancel(self, obj_id: str, objectType: int):
        form_data = {
            "kpn": "ACFUN_APP",
            "kpf": "PC_WEB",
            "subBiz": "mainApp",
            "interactType": 1,
            "objectType": objectType,
            "objectId": obj_id,
            "userId": self.uid,
        }
        form_data = self.update_token(form_data)
        req = self.client.post(source.apis['like_delete'], data=form_data)
        return req.json().get('result') == 1

    @need_login
    def throw_banana(self, ac_num, rt: int, count: int):
        api_req = self.client.post(source.apis['throw_banana'], data={
            "resourceId": ac_num,
            "count": 1 if 1 > count > 5 else count,
            "resourceType": rt
        }, headers={'referer': source.routes['index']})
        return api_req.json().get('result') == 0

    @need_login
    def follow_groups(self):
        api_req = self.client.get(source.apis['follow_groups'])
        api_data = api_req.json()
        if api_data.get('result') == 0:
            return api_data.get('groupList', [])
        return None

    def _follow_group_action(self, form_data: dict):
        api_req = self.client.post(source.apis['follow_group'], data=form_data)
        return api_req.json().get('result') == 0

    @need_login
    def follow_group_add(self, name: str):
        form_data = {"action": 4, "groupName": name}
        return self._follow_group_action(form_data)

    @need_login
    def follow_group_rename(self, gid: [int, str], name: str):
        form_data = {"action": 6, "groupId": gid, "groupName": name}
        return self._follow_group_action(form_data)

    @need_login
    def follow_group_remove(self, gid: [int, str]):
        form_data = {"action": 5, "groupId": gid}
        return self._follow_group_action(form_data)

    @need_login
    def follow_add(self, uid, attention: [bool, None] = None):
        form_data = {"toUserId": uid, "action": 1}
        if attention is True:
            form_data['action'] = 14
        elif attention is False:
            form_data['action'] = 15
        if form_data['action'] == 1:
            form_data['groupId'] = 0
        api_req = self.client.post(source.apis['follow'], data=form_data)
        return api_req.json().get('result') == 0

    @need_login
    def follow_remove(self, uid):
        form_data = {"toUserId": uid, "action": 2}
        api_req = self.client.post(source.apis['follow'], data=form_data)
        return api_req.json().get('result') == 0

    @need_login
    def history(self, page: int = 1, limit: int = 10, obj: bool = False):
        # 观看历史
        form_data = {"pageNo": page, "pageSize": limit, "resourceTypes": ''}
        api_req = self.client.post(source.apis['history'], data=form_data)
        api_data = api_req.json()
        if api_data.get('result') != 0:
            return None
        histories = api_data.get('histories', [])
        if obj is True:
            objs = list()
            for x in histories:
                if x.get('resourceType') == 1:
                    objs.append(self.AcBangumi(x.get('resourceId')))
                elif x.get('resourceType') == 2:
                    objs.append(self.AcVideo(x.get('resourceId'), x))
                elif x.get('resourceType') == 3:
                    objs.append(self.AcArticle(x.get('resourceId'), x))
            return objs
        return histories

    @need_login
    def my_fans(self, page: int = 1, limit: int = 10, obj: bool = False):
        # 粉丝列表
        form_data = {"page": page, "count": limit, "action": 8}
        api_req = self.client.post(source.apis['follow_fans'], data=form_data)
        api_data = api_req.json()
        if api_data.get('result') != 0:
            return None
        fans = api_data.get('friendList', [])
        if obj is True:
            return [self.AcUp(x) for x in fans]
        return fans

    def _get_my_posted(self,
                       rtype: int,
                       page: int = 1,
                       status: str = 'all',
                       sortby: str = 'recently',
                       keyword: [str, None] = None):
        # 我的文章
        status_list = {
            'all': 0,  # 全部
            'passed': 1,  # 已通过
            'posting': 2,  # 发布中
            'returned': 3,  # 已退回
        }
        sort_list = {
            'viwed': 1,  # 最多阅读
            'banana': 2,  # 最多香蕉
            'recently': 3,  # 最新发布
        }
        form_data = {
            "pcursor": 0 if (page - 1) < 0 else (page - 1),
            "resourceType": rtype,  # 2 视频 3 文章
            "authorId": self.uid,
            "sortType": sort_list.get(sortby, 3),
            "status": status_list.get(status, 0),
            "keyword": keyword,
        }
        api_req = self.client.post(source.apis['member_posted'], data=form_data)
        api_data = api_req.json()
        if api_data.get('result') == 0:
            return api_data.get('feed', [])
        return None

    @need_login
    def my_articles(self, page: int = 1, status: str = 'all', sortby: str = 'recently', keyword: [str, None] = None):
        return self._get_my_posted(3, page, status, sortby, keyword)

    @need_login
    def my_videos(self, page: int = 1, status: str = 'all', sortby: str = 'recently', keyword: [str, None] = None):
        return self._get_my_posted(2, page, status, sortby, keyword)

    @need_login
    def my_danmaku(self):
        # 弹幕管理
        pass

    @need_login
    def data_center(self, days: int = 1):
        api_req = self.client.post(source.apis['dataCenter_overview'], data={'days': 1 if days < 1 else days})
        api_data = api_req.json()
        if api_data.get('result') == 0:
            return api_data
        return None

    @need_login
    def data_center_detail(self, rtype: str, days: int = 1, sortby: str = 'viewCount'):
        rtypes = {'video': 2, 'article': 3, 'live': None}
        assert rtype in rtypes.keys()
        sort_list = {
            "viewCount": "阅读量",
            "commentCount": "评论量",
            "stowCount": "收藏量",
            "shareCount": "分享量",
            "bananaCount": "投蕉量"
        }
        assert sortby in sort_list
        form_data = {'days': 1 if days < 1 else days}
        if rtype == 'live':
            api_req = self.client.post(source.apis['dataCenter_live'], data=form_data)
        else:
            form_data.update({"resourceType": rtypes.get(rtype), "orderBy": sortby})
            api_req = self.client.post(source.apis['dataCenter_content'], data=form_data)
        api_data = api_req.json()
        if api_data.get('result') == 0:
            return api_data
        return None

    @need_login
    def get_live_config(self):
        param = {
            "kpn": "ACFUN_APP",
            "kpf": "PC_WEB",
            "userId": self.uid,
            "subBiz": "mainApp"
        }
        param = self.update_token(param)
        api_req = self.client.post(source.apis['live_obs_config'], params=param,
                                   headers={'referer': f"{source.scheme}://{source.domains['user']}"})
        return api_req.json()

    @need_login
    def post_article(self):
        # 发文章
        pass

    @need_login
    def post_video(self):
        # 发视频
        pass


class MyFavourite:
    folders = list()
    default_fid = None

    def __init__(self, acer):
        self.acer = acer
        self.video_groups()

    def add(self, obj_id: str, rType: int, fids: [str, None] = None):
        form_data = {"resourceId": obj_id, "resourceType": rType}
        if fids is not None or rType == 9:
            form_data['addFolderIds'] = str(fids or self.default_fid)
        req = self.acer.client.post(source.apis['favorite_add'], data=form_data,
                                    headers={"referer": source.routes['index']})
        return req.json().get('result') == 0

    def cancel(self, obj_id: str, rType: int, fids: [str, None] = None):
        form_data = {"resourceId": obj_id, "resourceType": rType}
        if fids is not None or rType == 9:
            form_data['delFolderIds'] = fids or self.default_fid
        req = self.acer.client.post(source.apis['favorite_remove'], data=form_data,
                                    headers={"referer": source.routes['index']})
        return req.json().get('result') == 0

    def video_groups(self):
        api_req = self.acer.client.get(source.apis['video_favorite_list'])
        api_data = api_req.json()
        if api_data.get('result') == 0:
            self.folders = api_data.get('dataList', [])
            self.default_fid = self.folders[0].get('folderId')
            return self.folders
        return None

    def video_group_add(self, name: str):
        form_data = {"name": name}
        api_req = self.acer.client.post(source.apis['video_favorite_group_add'], data=form_data,
                                        headers={"referer": source.routes['index']})
        return api_req.json().get('result') == 0

    def video_group_rename(self, fid: [int, str], name: str):
        form_data = {"folderId": fid, "name": name}
        api_req = self.acer.client.post(source.apis['video_favorite_group_update'], data=form_data,
                                        headers={"referer": source.routes['index']})
        return api_req.json().get('result') == 0

    def video_group_remove(self, fid: [int, str]):
        form_data = {"folderId": fid}
        api_req = self.acer.client.post(source.apis['video_favorite_group_delete'], data=form_data,
                                        headers={"referer": source.routes['index']})
        return api_req.json().get('result') == 0

    def video_list(self, fid: [int, str], page: int = 1, limit: int = 10):
        form_data = {"folderId": fid, "page": page, "perpage": limit}
        api_req = self.acer.client.post(source.apis['favorite_video'], data=form_data)
        data = api_req.json()
        if data.get('result') == 0:
            return data.get('favoriteList', [])
        return None

    def article_list(self, page: int = 1, limit: int = 10):
        form_data = {"page": page, "perpage": limit}
        api_req = self.acer.client.post(source.apis['favorite_article'], data=form_data)
        data = api_req.json()
        if data.get('result') == 0:
            return data.get('favoriteList', [])
        return None

    def bangumi_list(self, page: int = 1, limit: int = 10):
        param = {"page": page, "perpage": limit}
        api_req = self.acer.client.get(source.apis['favorite_article'], params=param)
        data = api_req.json()
        if data.get('result') == 0:
            return data.get('favoriteList', [])
        return None

    def album_list(self, page: int = 1, limit: int = 10):
        form_data = {"page": page, "perpage": limit}
        api_req = self.acer.client.post(source.apis['favorite_album'], data=form_data)
        data = api_req.json()
        if data.get('result') == 0:
            return data.get('favoriteList', [])
        return None

