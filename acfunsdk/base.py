# coding=utf-8
import os
import json
import httpx
from .page import *
from .exceptions import *

__author__ = 'dolacmeo'


class Acer:
    BASE_PATH = os.getcwd()
    client = None
    config = dict()

    is_logined = False
    did = None
    data = dict()
    tokens = dict()

    message = None
    follow = None
    favourite = None

    def __init__(self, **kwargs):
        self.config = kwargs
        self.client = httpx.Client(headers=source.header)
        self._get_personal()
        self.acfun = AcFun(self)

    def __repr__(self):
        show_name = (" " + self.username) or ''
        return f"Acer(#{self.uid or 'UNKNOWN'}{show_name})"

    @property
    def uid(self):
        return self.data.get('userId')

    @property
    def username(self):
        return self.data.get('userName')

    def get(self, url_str: str, title=None):
        return self.acfun.get(url_str, title)

    def _get_personal(self):
        live_page_req = self.client.get(source.routes['app'])
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
            self.data = info_data.get('info', {})
            self.message = MyMessage(self)
            self.follow = MyFollow(self)
            self.favourite = MyFavourite(self)
        else:
            api_req = self.client.post(source.apis['token_visitor'], data={"sid": "acfun.api.visitor"})
            api_data = api_req.json()
            assert api_data.get('result') == 0
            self.tokens = {
                "ssecurity": api_data.get("acSecurity", ''),
                "visitor_st": api_data.get("acfun.api.visitor_st", ''),
            }

    def update_token(self, data: dict):
        if self.is_logined:
            data.update({"acfun.midground.api_st": self.tokens['api_st']})
        else:
            data.update({"acfun.api.visitor_st": self.tokens['visitor_st']})
        return data

    def loading(self, username):
        cookie_data = open(f'{username}.cookies', 'rb').read()
        cookie = B64s(cookie_data, len(username)).b64decode()
        self.client.cookies.update(json.loads(cookie.decode()))
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
        return self.is_logined

    def logout(self):
        self.client.get(source.apis['logout'])
        self.client = httpx.Client(headers=source.header)
        self.is_logined = False
        self.data = dict()
        return True

    @need_login
    def setup_signature(self, text: str):
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

    @need_login
    def like(self, obj_id: str, object_type: int):
        form_data = {
            "kpn": "ACFUN_APP",
            "kpf": "PC_WEB",
            "subBiz": "mainApp",
            "interactType": 1,
            "objectType": object_type,
            "objectId": obj_id,
            "userId": self.uid,
        }
        form_data = self.update_token(form_data)
        req = self.client.post(source.apis['like_add'], data=form_data)
        return req.json().get('result') == 1

    @need_login
    def like_cancel(self, obj_id: str, object_type: int):
        form_data = {
            "kpn": "ACFUN_APP",
            "kpf": "PC_WEB",
            "subBiz": "mainApp",
            "interactType": 1,
            "objectType": object_type,
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
                    objs.append(self.acfun.AcBangumi(x.get('resourceId')))
                elif x.get('resourceType') == 2:
                    objs.append(self.acfun.AcVideo(x.get('resourceId'), x))
                elif x.get('resourceType') == 3:
                    objs.append(self.acfun.AcArticle(x.get('resourceId'), x))
            return objs
        return histories

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
