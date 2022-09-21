# coding=utf-8
from .utils import re, json, time, Bs
from .utils import AcSource, thin_string

__author__ = 'dolacmeo'


class Message:
    intro = None
    create_at = None
    whom = None
    raw_data = None
    raw_link = None

    def __init__(self, acer, **kwargs):
        self.acer = acer
        self.raw_data = kwargs
        self.raw_link = kwargs.get('content_url')
        self.intro = kwargs.get('intro')
        self.create_at = kwargs.get('create_at')
        if 'uid' in kwargs:
            self.whom = {'userId': kwargs.get('uid'), 'name': kwargs.get('username')}

    def __repr__(self):
        return f"AcMsg({self.intro})"

    def user(self):
        if self.whom is None:
            return None
        return self.acer.acfun.AcUp(self.whom)


class ReplyMsg(Message):

    def __init__(self, acer, **kwargs):
        self.content_title = kwargs.get('content_title', '')
        self.replied = kwargs.get('replied', '')
        self.content = kwargs.get('content', '')
        self.ncid = kwargs.get('ncid', '')
        self.username = kwargs.get('username', '')
        super().__init__(acer, **kwargs)

    def __repr__(self):
        return f"AcReply({self.content_title}—— {self.content} @{self.username})"

    def content(self):
        return self.acer.get(self.raw_data.get('content_url'))

    def replay(self):
        comments = self.content()._comment()
        return comments.find(self.raw_data.get('ncid'))


class LikeMsg(ReplyMsg):

    def __init__(self, acer, **kwargs):
        super().__init__(acer, **kwargs)

    def __repr__(self):
        return f"AcLike({self.replied} | @{self.username})"


class AtMsg(ReplyMsg):

    def __init__(self, acer, **kwargs):
        super().__init__(acer, **kwargs)

    def __repr__(self):
        return f"AcMsg({self.raw_link}#ncid={self.ncid} | @{self.username})"


class GiftMsg(Message):
    banana = 0

    def __init__(self, acer, **kwargs):
        self.content_title = kwargs.get('content_title', '')
        self.username = kwargs.get('username', '')
        self.banana = kwargs.get('banana', 0)
        super().__init__(acer, **kwargs)

    def __repr__(self):
        return f"AcGift({self.content_title} | 🍌x{self.banana} @{self.username})"


class NoticeMsg(Message):

    def __init__(self, acer, **kwargs):
        self.content_title = kwargs.get('content_title', '')
        super().__init__(acer, **kwargs)

    def __repr__(self):
        return f"AcNotice({self.content_title} >>> {self.raw_link})"


class SystemMsg(Message):
    classify = None

    def __init__(self, acer, **kwargs):
        super().__init__(acer, **kwargs)

    def __repr__(self):
        if 'up' in self.raw_data and '关注了你' in self.raw_data.get('intro', ''):
            link = self.raw_data.get('up', [])
            return f"AcFans(+1 | @{link[0]})"
        elif 'video' in self.raw_data and '已通过审核' in self.raw_data.get('intro', ''):
            link = self.raw_data.get('video', [])
            return f"AcPass({link[0]} 已通过审核)"
        elif 'article' in self.raw_data and '已通过审核' in self.raw_data.get('intro', ''):
            link = self.raw_data.get('article', [])
            return f"AcPass({link[0]} 已通过审核)"
        elif '有人收藏了你的' in self.raw_data.get('intro', ''):
            if 'video' in self.raw_data:
                link = self.raw_data.get('video', [])
            elif 'article' in self.raw_data:
                link = self.raw_data.get('article', [])
            else:
                return f"AcMsg({self.intro})"
            return f"AcStar(+1 | {link[0]})"
        return f"AcMsg({self.intro})"


class MyMessage:
    req_count = 0
    means = {
        'new_comment': '评论',
        'at_notify': '@我',
        'new_comment_like': '点赞',
        'new_gift': '礼物',
        'new_content_notify': '站内公告',
        'new_system_notify': '系统通知',
    }

    def __init__(self, acer):
        self.acer = acer

    def __repr__(self):
        msg = list()
        for k, v in self.unread.items():
            if v > 0:
                msg.append(f"{self.means[k]}[{v}]")
        return f"MyMessage({''.join(msg)})"

    @property
    def unread(self):
        if self.acer.is_logined is False:
            return None
        api_req = self.acer.client.get(AcSource.apis['unread'])
        api_data = api_req.json()
        if api_data.get('result') != 0:
            return None
        return api_data.get("unReadCount")

    def _get_msg_api(self, vid: str = '', page: int = 1):
        vids = ['', 'like', 'atmine', 'gift', 'sysmsg', 'resmsg']
        assert vid in vids
        self.req_count += 1
        param = {
            "quickViewId": 'upCollageMain',
            "reqID": self.req_count,
            "ajaxpipe": 1,
            "pageNum": page,
            "t": str(time.time_ns())[:13],
        }
        api_req = self.acer.client.get(AcSource.apis['message'] + vid, params=param)
        if api_req.text.endswith("/*<!-- fetch-stream -->*/"):
            api_data = json.loads(api_req.text[:-25])
            page_obj = Bs(api_data.get('html', ''), 'lxml')
        else:
            return None
        item_data = list()
        total = str(page_obj.select_one('#listview').attrs['totalcount'])
        for item in page_obj.select('#listview > ul,.main-block-msg-item'):
            if vid == '':
                main_url = AcSource.scheme + ':' + item.select_one('.intro').a.attrs['href']
                reply_url = item.select_one('a.msg-reply').attrs['href']
                item_data.append({
                    'content_url': main_url,
                    'content_title': item.select_one('.intro').a.text.strip(),
                    'replied': item.select_one('.msg-replied .inner').text.strip().replace('\xa0', ' '),
                    'uid': item.select_one('.titlebar .name').attrs['href'][17:],
                    'username': item.select_one('.titlebar .name').text,
                    'create_at': item.select_one('.titlebar .time').text.strip(),
                    'ncid': reply_url.split('#ncid=')[1],
                    'content': item.select_one('.msg-reply .inner').text.strip().replace('\xa0', ' '),
                    'intro': item.select_one('.content .intro').text.strip(),
                })
            elif vid == 'like':
                this_url = item.select_one('a.replied').attrs['href'].split('#')
                main_url = AcSource.scheme + ':' + this_url[0]
                item_data.append({
                    'content_url': main_url,
                    'replied': item.select_one('.clamp-text .inner').text.strip().replace('\xa0', ' '),
                    'uid': item.select_one('.titlebar .name').attrs['href'][17:],
                    'username': item.select_one('.titlebar .name').text,
                    'ncid': this_url[1][5:],
                    'create_at': item.select_one('.titlebar span.time').text.strip(),
                    'intro': item.select_one('.titlebar').text.strip(),
                })
            elif vid == 'atmine':
                this_url = item.select_one('.content .msg-text').attrs['href']
                item_data.append({
                    'content_url': AcSource.scheme + ':' + this_url.split('#')[0],
                    'ncid': this_url.split('#ncid=')[1],
                    'uid': item.select_one('.avatar-section').attrs['href'][17:],
                    'username': item.select_one('.titlebar-container .name').text,
                    'create_at': item.select_one('.titlebar-container span.time').text.strip(),
                    'intro': item.select_one('.titlebar-container .intro').text.strip(),
                })
            elif vid == 'gift':
                if 'moment-gift' in item.attrs['class']:
                    this_url = item.select_one('.msg-content').a.attrs['href']
                    intro = thin_string(item.select_one('.msg-content').text)
                    item_data.append({
                        'classify': 'moment',
                        'content_url': AcSource.scheme + ':' + this_url,
                        'content_title': '动态',
                        'uid': item.select_one('.avatar-section').attrs['href'][17:],
                        'username': item.select_one('.content .name').text,
                        'create_at': item.select_one('.content span.time').text.strip(),
                        'intro': intro,
                        'banana': int(re.findall(r'(\d)根香蕉', intro)[0])
                    })
                else:
                    acer_url = item.select_one('p a:nth-of-type(1)')
                    this_url = item.select_one('p a:nth-of-type(2)')
                    intro = thin_string(item.select_one('p').text)
                    item_data.append({
                        'classify': 'content',
                        'content_url': AcSource.scheme + ':' + this_url.attrs['href'],
                        'content_title': this_url.text,
                        'uid': acer_url.attrs['href'][17:],
                        'username': acer_url.text,
                        'create_at': item.select_one('.msg-item-time').text.strip(),
                        'intro': intro,
                        'banana': int(re.findall(r'(\d)根香蕉', intro)[0])
                    })
            elif vid == 'sysmsg':
                this_title = item.select_one('div:nth-of-type(1)').text.strip()
                this_content = item.select_one('div:nth-of-type(2)').get_text("|", strip=True)
                this_content = "\n".join([text for text in this_content.split("|") if not text.startswith('http')])
                this_content = re.sub('(>{2,})', '', this_content)
                this_link = item.select_one('div:nth-of-type(2)').a.attrs['href']
                item_data.append({
                    'content_url': this_link,
                    'content_title': this_title,
                    'create_at': item.select_one('.msg-item-time').text.strip(),
                    'intro': thin_string(this_content),
                })
            elif vid == 'resmsg':
                intro = item.select_one('p:nth-of-type(1)').text.strip()
                links = dict()
                for link in item.select('a'):
                    url_str = link.attrs['href']
                    if not url_str.startswith('http'):
                        url_str = AcSource.scheme + ':' + url_str
                    for link_name in ['video', 'article', 'album', 'bangumi', 'up', 'live']:
                        if url_str.startswith(AcSource.routes[link_name]) and link_name not in links:
                            links[link_name] = [link.text, url_str]
                item_data.append({
                    'create_at': item.select_one('p.msg-item-time').text.strip(),
                    'intro': thin_string(intro, True),
                    **links
                })
        return item_data, total

    def reply(self, page: int = 1, obj: bool = False):
        api_data, total = self._get_msg_api('', page)
        if obj is True:
            return [ReplyMsg(self, **i) for i in api_data]
        return api_data

    def like(self, page: int = 1, obj: bool = False):
        api_data, total = self._get_msg_api('like', page)
        if obj is True:
            return [LikeMsg(self, **i) for i in api_data]
        return api_data

    def at(self, page: int = 1, obj: bool = False):
        api_data, total = self._get_msg_api('atmine', page)
        if obj is True:
            return [AtMsg(self, **i) for i in api_data]
        return api_data

    def gift(self, page: int = 1, obj: bool = False):
        api_data, total = self._get_msg_api('gift', page)
        if obj is True:
            return [GiftMsg(self, **i) for i in api_data]
        return api_data

    def notice(self, page: int = 1, obj: bool = False):
        api_data, total = self._get_msg_api('sysmsg', page)
        if obj is True:
            return [NoticeMsg(self, **i) for i in api_data]
        return api_data

    def system(self, page: int = 1, obj: bool = False):
        api_data, total = self._get_msg_api('resmsg', page)
        if obj is True:
            return [SystemMsg(self, **i) for i in api_data]
        return api_data
