# coding=utf-8
from .utils import json, Literal
from .utils import AcSource

__author__ = 'dolacmeo'


class MyFansClub:

    def __init__(self, acer):
        self.acer = acer

    @property
    def referer(self):
        return f"{AcSource.routes['medallist']}"

    def medal_list(self):
        api_req = self.acer.client.post(AcSource.apis['live_medal_list'])
        api_data = api_req.json()
        assert api_data.get("result") == 0
        return api_data.get("medalList")

    def medal_info(self, uid: [str, int]):
        api_req = self.acer.client.post(AcSource.apis['live_medal'], params={"uperId": uid})
        api_data = api_req.json()
        assert api_data.get("result") == 0
        return api_data

    def medal_wear(self, uid: [str, int], on_off: bool):
        param = {"uperId": uid}
        on_off = "on" if on_off is True else "off"
        api_req = self.acer.client.post(AcSource.apis[f"live_medal_wear_{on_off}"], params=param)
        api_data = api_req.json()
        assert api_data.get("result") == 0
        return api_data


class MyFollow:

    def __init__(self, acer):
        self.acer = acer
        pass

    @property
    def referer(self):
        return f"{AcSource.routes['member_following']}"

    def groups(self):
        api_req = self.acer.client.get(AcSource.apis['follow_groups'])
        api_data = api_req.json()
        if api_data.get('result') == 0:
            return api_data.get('groupList', [])
        return None

    def _follow_group_action(self, form_data: dict):
        api_req = self.acer.client.post(AcSource.apis['follow_group'], data=form_data)
        return api_req.json().get('result') == 0

    def group_add(self, name: str):
        form_data = {"action": 4, "groupName": name}
        return self._follow_group_action(form_data)

    def group_rename(self, gid: [int, str], name: str):
        form_data = {"action": 6, "groupId": gid, "groupName": name}
        return self._follow_group_action(form_data)

    def group_remove(self, gid: [int, str]):
        form_data = {"action": 5, "groupId": gid}
        return self._follow_group_action(form_data)

    def add(self, uid, attention: [bool, None] = None):
        form_data = {"toUserId": uid, "action": 1}
        if attention is True:
            form_data['action'] = 14
        elif attention is False:
            form_data['action'] = 15
        if form_data['action'] == 1:
            form_data['groupId'] = 0
        api_req = self.acer.client.post(AcSource.apis['follow'], data=form_data)
        return api_req.json().get('result') == 0

    def remove(self, uid):
        form_data = {"toUserId": uid, "action": 2}
        api_req = self.acer.client.post(AcSource.apis['follow'], data=form_data)
        return api_req.json().get('result') == 0

    def my_fans(self, page: int = 1, limit: int = 10, obj: bool = False):
        form_data = {"page": page, "count": limit, "action": 8}
        api_req = self.acer.client.post(AcSource.apis['follow_fans'], data=form_data)
        api_data = api_req.json()
        if api_data.get('result') != 0:
            return None
        fans = api_data.get('friendList', [])
        if obj is True:
            return [self.acer.acfun.AcUp(x) for x in fans]
        return fans


class MyFavourite:
    folders = list()
    default_fid = None

    def __init__(self, acer):
        self.acer = acer
        self.video_groups()

    @property
    def referer(self):
        return f"{AcSource.routes['member_favourite']}"

    def add(self, rtype: int, rid: str, fids: [str, None] = None):
        rtype = {"2": 9}.get(str(rtype), int(rtype))
        form_data = {"resourceId": rid, "resourceType": rtype}
        if fids is not None or rtype == 9:
            form_data['addFolderIds'] = str(fids or self.default_fid)
        req = self.acer.client.post(AcSource.apis['favorite_add'], data=form_data,
                                    headers={"referer": AcSource.routes['index']})
        return req.json().get('result') == 0

    def cancel(self, rtype: int, rid: str, fids: [str, None] = None):
        rtype = {"2": 9}.get(str(rtype), int(rtype))
        form_data = {"resourceId": rid, "resourceType": rtype}
        if fids is not None or rtype == 9:
            form_data['delFolderIds'] = fids or self.default_fid
        req = self.acer.client.post(AcSource.apis['favorite_remove'], data=form_data,
                                    headers={"referer": AcSource.routes['index']})
        return req.json().get('result') == 0

    def video_groups(self):
        api_req = self.acer.client.get(AcSource.apis['favorite_list'])
        api_data = api_req.json()
        if api_data.get('result') == 0:
            self.folders = api_data.get('dataList', [])
            self.default_fid = self.folders[0].get('folderId')
            return self.folders
        return None

    def video_group_add(self, name: str):
        form_data = {"name": name}
        api_req = self.acer.client.post(AcSource.apis['favorite_group_add'], data=form_data,
                                        headers={"referer": AcSource.routes['index']})
        return api_req.json().get('result') == 0

    def video_group_rename(self, fid: [int, str], name: str):
        form_data = {"folderId": fid, "name": name}
        api_req = self.acer.client.post(AcSource.apis['favorite_group_update'], data=form_data,
                                        headers={"referer": AcSource.routes['index']})
        return api_req.json().get('result') == 0

    def video_group_remove(self, fid: [int, str]):
        form_data = {"folderId": fid}
        api_req = self.acer.client.post(AcSource.apis['favorite_group_delete'], data=form_data,
                                        headers={"referer": AcSource.routes['index']})
        return api_req.json().get('result') == 0

    def video_list(self, fid: [int, str], page: int = 1, limit: int = 10):
        form_data = {"folderId": fid, "page": page, "perpage": limit}
        api_req = self.acer.client.post(AcSource.apis['favorite_video'], data=form_data)
        data = api_req.json()
        if data.get('result') == 0:
            return data.get('favoriteList', [])
        return None

    def article_list(self, page: int = 1, limit: int = 10):
        form_data = {"page": page, "perpage": limit}
        api_req = self.acer.client.post(AcSource.apis['favorite_article'], data=form_data)
        data = api_req.json()
        if data.get('result') == 0:
            return data.get('favoriteList', [])
        return None

    def bangumi_list(self, page: int = 1, limit: int = 10):
        param = {"page": page, "perpage": limit}
        api_req = self.acer.client.get(AcSource.apis['favorite_article'], params=param)
        data = api_req.json()
        if data.get('result') == 0:
            return data.get('favoriteList', [])
        return None

    def album_list(self, page: int = 1, limit: int = 10):
        form_data = {"page": page, "perpage": limit}
        api_req = self.acer.client.post(AcSource.apis['favorite_album'], data=form_data)
        data = api_req.json()
        if data.get('result') == 0:
            return data.get('favoriteList', [])
        return None


class MyAlbum:

    def __init__(self, acer):
        self.acer = acer

    @property
    def referer(self):
        return f"{AcSource.routes['member_album']}"

    def list(self, page: int = 1, size: int = 10):
        param = {"size": size, "page": page, "status": 0, "sort": 0}
        api_req = self.acer.client.get(AcSource.apis["my_album_list"], params=param)
        api_data = api_req.json()
        assert api_data.get("result") == 0
        return api_data

    def add(self, title: str, rtype: Literal[2, 3], cover: str, intro: str, status: Literal[1, 2]):
        form = {
            "title": title,
            "resourceType": rtype,
            "coverImage": cover,
            "intro": intro,
            "status": status,
        }
        api_req = self.acer.client.post(AcSource.apis["my_album_add"], data=form)
        api_data = api_req.json()
        assert api_data.get("result") == 0
        return api_data.get("arubamuId")

    def remove(self, album_id: [str, int]):
        api_req = self.acer.client.post(AcSource.apis["my_album_del"], data={"arubamuId": album_id})
        api_data = api_req.json()
        return api_data.get("result") == 0

    def update(self, album_id: [str, int], title: str, rtype: Literal[2, 3],
               cover: str, intro: str, status: Literal[1, 2]):
        form = {
            "arubamuId": album_id,
            "title": title,
            "resourceType": rtype,
            "coverImage": cover,
            "intro": intro,
            "status": status,
        }
        api_req = self.acer.client.post(AcSource.apis["my_album_update"], data=form)
        api_data = api_req.json()
        return api_data.get("result") == 0

    def get_contents(self, album_id: [str, int], page: int = 1, size: int = 10):
        param = {"arubamuId": album_id, "page": page, "size": size}
        api_req = self.acer.client.get(AcSource.apis["my_album_contents"], params=param)
        api_data = api_req.json()
        assert api_data.get("result") == 0
        return api_data

    def contents_add(self, album_id: [str, int], rtype: Literal[2, 3], rids: [str, list]):
        if isinstance(rids, str):
            rids = rids.split(',')
        rlist = [{"resourceId": x, "resourceType": rtype} for x in rids]
        form = {
            "arubamuId": album_id,
            "resourceListStr": json.dumps(rlist, separators=(',', ':'))
        }
        api_req = self.acer.client.post(AcSource.apis["my_album_content_add"], data=form)
        api_data = api_req.json()
        return api_data.get("result") == 0

    def contents_del(self, album_id: [str, int], rids: [str, list]):
        if isinstance(rids, str):
            rids = rids.split(',')
        form = {
            "arubamuId": album_id,
            "arubamuContentIdList": rids
        }
        api_req = self.acer.client.post(AcSource.apis["my_album_content_del"], data=form)
        api_data = api_req.json()
        return api_data.get("result") == 0


class MyContribute:

    def __init__(self, acer):
        self.acer = acer

    @property
    def referer(self):
        return f"{AcSource.routes['up_index']}"

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
            "authorId": self.acer.uid,
            "sortType": sort_list.get(sortby, 3),
            "status": status_list.get(status, 0),
            "keyword": keyword,
        }
        api_req = self.acer.client.post(AcSource.apis['member_posted'], data=form_data)
        api_data = api_req.json()
        if api_data.get('result') == 0:
            return api_data.get('feed', [])
        return None

    def my_articles(self, page: int = 1, status: str = 'all', sortby: str = 'recently', keyword: [str, None] = None):
        return self._get_my_posted(3, page, status, sortby, keyword)

    def my_videos(self, page: int = 1, status: str = 'all', sortby: str = 'recently', keyword: [str, None] = None):
        return self._get_my_posted(2, page, status, sortby, keyword)

    def data_center(self, days: int = 1):
        api_req = self.acer.client.post(AcSource.apis['dataCenter_overview'], data={'days': 1 if days < 1 else days})
        api_data = api_req.json()
        if api_data.get('result') == 0:
            return api_data
        return None

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
            api_req = self.acer.client.post(AcSource.apis['dataCenter_live'], data=form_data)
        else:
            form_data.update({"resourceType": rtypes.get(rtype), "orderBy": sortby})
            api_req = self.acer.client.post(AcSource.apis['dataCenter_content'], data=form_data)
        api_data = api_req.json()
        if api_data.get('result') == 0:
            return api_data
        return None

    def get_live_config(self):
        param = {
            "kpn": "ACFUN_APP",
            "kpf": "PC_WEB",
            "userId": self.acer.uid,
            "subBiz": "mainApp"
        }
        param = self.acer.update_token(param)
        api_req = self.acer.client.post(AcSource.apis['live_obs_config'], params=param,
                                        headers={'referer': f"{AcSource.routes['member_index']}"})
        return api_req.json()

    def post_article(self):
        # 发文章
        pass

    def post_video(self):
        # 发视频
        pass


class MyDanmaku:

    def __init__(self, acer):
        self.acer = acer

    @property
    def referer(self):
        return f"{AcSource.routes['danmaku_manage']}"

    def advance_config(self):
        api_req = self.acer.client.post(AcSource.apis['danmaku_config'])
        api_data = api_req.json()
        assert api_data.get("result") == 0
        return api_data

    def advance_setup(self, n: Literal['1', '2', '3', '4', 1, 2, 3, 4]):
        """
        https://member.acfun.cn/inter-active/danmaku-setting
        1 任何人
        2 仅限粉丝
        3 仅限互相关注
        4 关闭高级弹幕
        """
        api_req = self.acer.client.post(AcSource.apis['danmaku_setup'], data={"availableType": str(n)})
        api_data = api_req.json()
        return api_data.get("result") == 0

    def forbidden_words(self):
        api_req = self.acer.client.post(AcSource.apis['ban_danmaku'])
        api_data = api_req.json()
        assert api_data.get("result") == 0
        return api_data.get("data")

    def forbidden_add(self, words: str):
        api_req = self.acer.client.post(AcSource.apis['ban_danmaku_add'], data={"forbiddenWords": words})
        api_data = api_req.json()
        return api_data.get("result") == 0

    def forbidden_del(self, words: str):
        api_req = self.acer.client.post(AcSource.apis['ban_danmaku_del'], data={"forbiddenWords": words})
        api_data = api_req.json()
        return api_data.get("result") == 0

    def advance_list(self,
                     page: int = 1,
                     ac_num: [int, str, None] = None,
                     vid: [int, str, None] = None,
                     search: [str, None] = None):
        form = {
            "dougaId": ac_num or "",
            "videoId": vid or "",
            "danmakuText": search or "",
            "page": page,
        }
        api_req = self.acer.client.post(AcSource.apis['search_danmaku_adv'], data=form)
        api_data = api_req.json()
        assert api_data.get("result") == 0
        return api_data

    def danmaku_list(self,
                     page: int = 1,
                     ac_num: [int, str, None] = None,
                     vid: [int, str, None] = None,
                     search: [str, None] = None):
        form = {
            "dougaId": ac_num or "",
            "videoId": vid or "",
            "danmakuText": search or "",
            "page": page,
        }
        api_req = self.acer.client.post(AcSource.apis['search_danmaku'], data=form)
        api_data = api_req.json()
        assert api_data.get("result") == 0
        return api_data

    def danmaku_protect(self, ac_num: [int, str], danmaku_id: [int, str], on_off: bool = True):
        form = {
            "videoResourceType": "douga",
            "videoResourceId": ac_num,
            "danmakuId": danmaku_id,
            "rank": 9 if on_off is True else 5,
        }
        api_req = self.acer.client.post(AcSource.apis['protect_danmaku'], data=form)
        api_data = api_req.json()
        assert api_data.get("result") == 0
        return api_data

    def danmaku_del(self, danmaku_ids: [int, str]):
        form = {"danmakuIdList": str(danmaku_ids)}
        api_req = self.acer.client.post(AcSource.apis['delete_danmaku'], data=form)
        api_data = api_req.json()
        assert api_data.get("result") == 0
        return api_data


class BananaMall:

    def __init__(self, acer):
        self.acer = acer

    @property
    def referer(self):
        return f"{AcSource.routes['member_mall']}"

    def shop_list(self, page: int = 1, size: int = 30, stype: Literal[1, 2, 3] = 1, asc: bool = False):
        form = {"pageNo": page, "pageSize": size, "sortType": stype, "asc": asc}
        api_req = self.acer.client.post(AcSource.apis['shop_list'], data=form)
        api_data = api_req.json()
        assert api_data.get("result") == 0
        return api_data

    def my_items(self, page: int = 1, size: int = 30):
        param = {"page": page, "count": size}
        api_req = self.acer.client.get(AcSource.apis['shop_user_item'], params=param)
        api_data = api_req.json()
        assert api_data.get("result") == 0
        return api_data

    def set_item(self, pid: int, on_off: bool = True):
        form = {"productId": pid}
        on_off = "use" if on_off is True else "unuse"
        api_req = self.acer.client.post(AcSource.apis[f"shop_user_item_{on_off}"], data=form)
        api_data = api_req.json()
        return api_data.get("result") == 0

    def my_orders(self):
        # https://www.acfun.cn/member/mall?tab=orders
        # 缺少足够样本获取翻页接口请求
        raise PermissionError("接口未知：缺少足够样本获取翻页接口请求")
