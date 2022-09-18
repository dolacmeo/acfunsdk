# coding=utf-8
import time
from rich.progress import Progress
from acfunsdk.source import routes, apis
from acfunsdk.exceptions import *


class AcComment:
    resource_type_map = {
        "1": 6,  # 番剧
        "2": 3,  # 视频稿件
        "3": 1,  # 文章稿件
        "10": 4,  # 动态
    }

    sourceId = None
    hot_comments = list()
    root_comments = list()
    sub_comments = dict()
    commentIds = list()
    commentsMap = dict()

    def __init__(self, acer, rtype: [str, int], rid: [str, int]):
        self.acer = acer
        self.sourceId = str(rid)
        self.sourceType = self.resource_type_map[str(rtype)]
        self.main = self.acer.acfun.resource(rtype, rid)

    def __repr__(self):
        return f"AcComment([ac{self.sourceId}] Σ{len(self.root_comments)})"

    @property
    def referer(self):
        return self.main.referer

    def _get_data(self, page: int = 1, api_name: str = 'comment'):
        assert api_name in ['comment', 'comment_floor']
        param = {
            "sourceId": self.sourceId,
            "sourceType": self.sourceType,
            "page": page,
            "pivotCommentId": 0,
            "newPivotCommentId": "",
            "t": str(time.time_ns())[:13],
            "supportZtEmot": True,
        }
        req = self.acer.client.get(apis[api_name], params=param)
        return req.json()

    def _get_sub(self, root_id, page: int = 1):
        param = {
            "sourceId": self.sourceId,
            "sourceType": self.sourceType,
            "rootCommentId": root_id,
            "page": page,
            "t": str(time.time_ns())[:13],
            "supportZtEmot": True
        }
        req = self.acer.client.get(apis['comment_subs'], params=param)
        return req.json()

    def get_all_comment(self):
        self.hot_comments = list()
        self.root_comments = list()
        self.sub_comments = dict()
        page = 1
        page_max = 10
        with Progress() as pp:
            comments = pp.add_task("AcComment", total=page_max)
            while page <= page_max:
                api_data = self._get_data(page)
                if api_data.get('result') != 0:
                    print(api_data)
                    break
                self.hot_comments.extend(api_data.get('hotComments', []))
                self.root_comments.extend(api_data.get('rootComments', []))
                self.sub_comments.update(api_data.get('subCommentsMap', {}))
                page_max = api_data.get('totalPage', page)
                page = api_data.get('curPage', 1)
                page += 1
                pp.update(comments, total=page_max, completed=page)
            pp.update(comments, total=page_max, completed=page_max)
            pp.stop()

        for rid, sub_data in self.sub_comments.items():
            while sub_data['pcursor'] != "no_more":
                sub_page = self._get_sub(rid, sub_data['pcursor'])
                if 'subComments' not in sub_page:
                    sub_data['pcursor'] = "no_more"
                    break
                sub_data['subComments'].extend(sub_page['subComments'])
                if sub_page['curPage'] < sub_page['totalPage']:
                    sub_data['pcursor'] += 1
                else:
                    sub_data['pcursor'] = "no_more"
                time.sleep(0.1)

    def get_all_floors(self):
        first_page = self._get_data(1, 'comment_floor')
        self.commentIds = first_page['commentIds']
        self.commentsMap = first_page['commentsMap']
        page = first_page['curPage']
        page_max = first_page['totalPage']
        while page <= page_max:
            page += 1
            api_data = self._get_data(page, 'comment_floor')
            assert api_data['result'] == 0
            self.commentIds.extend(api_data['commentIds'])
            self.commentsMap.update(api_data['commentsMap'])
            time.sleep(0.5)

    @need_login
    def add(self, content: str, reply_id: [str, int, None] = None):
        form_data = {
            "sourceId": self.sourceId,
            "sourceType": self.sourceType,
            "content": content,
            "replyToCommentId": reply_id or "",
        }
        req = self.acer.client.post(apis['comment_add'], data=form_data,
                                    headers={'referer': self.referer})
        return req.json().get('result') == 0

    @need_login
    def delete(self, floor: int):
        this_comment = None
        for c in self.root_comments:
            if c.get('floor') == floor:
                this_comment = Comment(self.acer, c, self)
                break
        if this_comment is None:
            return False
        return this_comment.delete()

    def hot(self):
        datas = list()
        for c in self.hot_comments:
            datas.append(Comment(self.acer, c, self))
        return datas

    def list(self):
        datas = list()
        for c in self.root_comments:
            datas.append(Comment(self.acer, c, self))
        return datas

    def get(self, floor: int):
        for x in self.root_comments:
            if x['floor'] == floor:
                return Comment(self.acer, x, self)
        return None

    def find(self, cid: [int, str]):
        for x in self.root_comments:
            if x['commentId'] == int(cid):
                return Comment(self.acer, x, self)
        for x in self.sub_comments.values():
            for y in x.get('subComments', []):
                if y['commentId'] == int(cid):
                    return Comment(self.acer, y, self)
        return None


class Comment:
    data = dict()
    ac_num = None

    def __init__(self, acer, data: dict, main_obj: AcComment):
        self.acer = acer
        self.data = data
        self.ac_num = self.data.get('sourceId')
        self.main_obj = main_obj
        self.referer = self.main_obj.referer or f"{routes['index']}"

    def cdata(self, name):
        return self.data.get(name)

    def up(self):
        return self.acer.acfun.AcUp(self.cdata('userId'))

    def __repr__(self):
        content = self.data.get('content', '').replace('\r\n', '↲  ').replace('\n', '↲  ')
        return f"C([{self.cdata('commentId')}]#{self.cdata('floor')} {content} " \
               f"@{self.cdata('userName')}[{self.cdata('userId')}])"

    @property
    def api_data(self):
        return {
            "sourceId": self.data.get('sourceId'),
            "sourceType": self.data.get('sourceType'),
            "commentId": self.data.get('commentId'),
        }

    @need_login
    def like(self):
        if self.cdata('isLiked') is False:
            req = self.acer.client.post(apis['comment_like'], data=self.api_data, headers={'referer': self.referer})
            return req.json().get('result') == 0
        return True

    @need_login
    def unlike(self):
        if self.cdata('isLiked') is True:
            req = self.acer.client.post(apis['comment_unlike'], data=self.api_data, headers={'referer': self.referer})
            return req.json().get('result') == 0
        return True

    @need_login
    def delete(self):
        req = self.acer.client.post(apis['comment_delete'], data=self.api_data, headers={'referer': self.referer})
        return req.json().get('result') == 0
