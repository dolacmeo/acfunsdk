# coding=utf-8
import os
import json
from typing import Literal
from .page import *
from .exceptions import need_login

__author__ = 'dolacmeo'


class Acer:
    BASE_PATH = os.getcwd()
    client = None
    config = dict()

    did = None
    data = dict()
    tokens = dict()

    is_logined = False
    message = None
    fansclub = None
    moment = None
    follow = None
    favourite = None
    album = None
    contribute = None
    danmaku = None
    bananamall = None

    def __init__(self, **kwargs):
        self.config = kwargs
        self.client = httpx.Client(headers=AcSource.header)
        if "loading" in kwargs:
            self.loading(kwargs['loading'])
        elif "username" in kwargs and "password" in kwargs:
            self.login(kwargs['username'], kwargs['password'])
        else:
            self._get_personal()
        self.acfun = AcFun(self)

    def __repr__(self):
        if self.is_logined:
            return f"Acer(#{self.uid}@{self.username})"
        return f"Acer(#UNKNOWN)"

    @property
    def referer(self):
        return f"{AcSource.routes['member']}"

    @property
    def uid(self):
        return self.data.get('userId')

    @property
    def username(self):
        return self.data.get('userName')

    def get(self, url_str: str, title=None):
        return self.acfun.get(url_str, title)

    def _get_personal(self):
        live_page_req = self.client.get(AcSource.routes['app'])
        assert live_page_req.status_code // 100 == 2
        self.did = live_page_req.cookies.get('_did')
        if self.is_logined:
            api_req = self.client.post(AcSource.apis['token'], data={"sid": "acfun.midground.api"})
            api_data = api_req.json()
            assert api_data.get('result') == 0
            self.tokens = {
                "ssecurity": api_data.get("ssecurity", ''),
                "api_st": api_data.get("acfun.midground.api_st", ''),
                "api_at": api_data.get("acfun.midground.api.at", ''),
            }
            info_req = self.client.get(AcSource.apis['personalInfo'])
            info_data = info_req.json()
            assert info_data.get('result') == 0
            self.data = info_data.get('info', {})
            self.message = MyMessage(self)
            self.fansclub = MyFansClub(self)
            self.moment = MyMoment(self)
            self.follow = MyFollow(self)
            self.favourite = MyFavourite(self)
            self.album = MyAlbum(self)
            self.contribute = MyContribute(self)
            self.danmaku = MyDanmaku(self)
            self.bananamall = BananaMall(self)
            self.signin()  # 自动签到
        else:
            api_req = self.client.post(AcSource.apis['token_visitor'], data={"sid": "acfun.api.visitor"})
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
        api_req = self.client.post(AcSource.apis['login'], data=form_data)
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
        self.client.get(AcSource.apis['logout'])
        self.client = httpx.Client(headers=AcSource.header)
        self.is_logined = False
        self.data = dict()
        self.tokens = dict()
        self.message = None
        self.fansclub = None
        self.moment = None
        self.follow = None
        self.favourite = None
        self.album = None
        self.contribute = None
        self.danmaku = None
        self.bananamall = None
        return True

    @need_login
    def acoin(self):
        req = self.client.get(AcSource.apis['acoinBalance'])
        data = req.json()
        if data.get('result') == 0:
            return data.get('data')
        return None

    @need_login
    def setup_signature(self, text: str):
        api_req = self.client.post(AcSource.apis['updateSignature'], data={'signature': text},
                                   headers={'referer': 'https://www.acfun.cn/member/setting?tab=info'})
        return api_req.json().get('result') == 0

    @need_login
    def signin(self):
        if self.data.get("signIn") is True:
            return True
        api_req = self.client.get(AcSource.apis['signIn'])
        api_data = api_req.json()
        return api_data.get('result') == 0

    @need_login
    def throw_banana(self, rtype, rid, count: int):
        api_req = self.client.post(AcSource.apis['throw_banana'], data={
            "count": 1 if 1 > count > 5 else count,
            "resourceId": rid,
            "resourceType": rtype
        }, headers={'referer': AcSource.routes['index']})
        return api_req.json().get('result') == 0

    def _like(self, on_off: bool, otype, oid):
        otype = {"1": 18}.get(str(otype), int(otype))  # 番剧
        form_data = {
            "kpn": "ACFUN_APP",
            "kpf": "PC_WEB",
            "subBiz": "mainApp",
            "interactType": 1,
            "objectType": otype,
            "objectId": oid,
            "userId": self.uid,
        }
        form_data = self.update_token(form_data)
        x = "like_add" if on_off is True else "like_delete"
        req = self.client.post(AcSource.apis[x], data=form_data)
        return req.json().get('result') == 1

    @need_login
    def like_add(self, otype, oid):
        return self._like(True, otype, oid)

    @need_login
    def like_delete(self, otype, oid):
        return self._like(False, otype, oid)

    @need_login
    def history(self, page: int = 1, limit: int = 10, obj: bool = False):
        form_data = {"pageNo": page, "pageSize": limit, "resourceTypes": ''}
        api_req = self.client.post(AcSource.apis['history'], data=form_data)
        api_data = api_req.json()
        assert api_data.get('result') == 0
        if obj is False:
            return api_data
        objs = list()
        for x in api_data.get('histories', []):
            rtype, rid = x.get('resourceType'), x.get('resourceId')
            if rtype in range(1, 4):
                objs.append(self.acfun.resource(rtype, rid))
        api_data['histories'] = objs
        return api_data

    @need_login
    def history_del_all(self, rtype: Literal["", "1,2", "3"] = ""):
        # 空 全部;1,2 视频;3 文章
        form_data = {"resourceTypes": rtype or ''}
        api_req = self.client.post(AcSource.apis['history'], data=form_data)
        api_data = api_req.json()
        return api_data.get('result') == 0
