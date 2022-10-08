# coding=utf-8
from .utils import os, json, time, subprocess, parse
from .utils import AcSource, need_login, emoji_cleanup

__author__ = 'dolacmeo'


class AcLive:
    last_update = None
    raw_data = dict()

    def __init__(self, acer):
        self.acer = acer
        self._get_list()

    @property
    def referer(self):
        return f"{AcSource.routes['live_index']}"

    def __repr__(self):
        return f"AcLive(直播 - AcFun弹幕视频网)"

    def _get_list(self):
        if self.last_update is None or time.time() - self.last_update >= 60:
            api_req = self.acer.client.get(AcSource.apis['live_list'])
            self.raw_data = api_req.json()
            self.last_update = time.time()

    def list(self, obj: bool = False) -> (list, None):
        self._get_list()
        if obj is False:
            return self.raw_data.get("liveList")
        lives = list()
        for x in self.raw_data.get('liveList', []):
            lives.append(AcLiveUp(self.acer, x.get('authorId'), x))
        return lives

    def get(self, uid: [int, str]):
        return AcLiveUp(self.acer, uid)


class LiveItem:
    raw_data = None
    is_open = False
    liveId = None
    enterRoomAttach = None
    availableTickets = []
    representation = []

    def __init__(self, acer, uid: int, parent):
        self.acer = acer
        self.uid = uid
        self.parent = parent
        self.loading()

    def loading(self):
        form_data = {"authorId": self.uid, "pullStreamType": "FLV"}
        api_data = self.parent._api_action('live_play', form_data)
        if api_data.get('result') == 129004:
            self.is_open = False
            return False
        elif api_data.get('result') != 1:
            return False
        self.is_open = True
        self.raw_data = api_data['data']
        self.liveId = api_data['data'].get("liveId")
        self.availableTickets = api_data['data'].get("availableTickets", [])
        self.enterRoomAttach = api_data['data'].get("enterRoomAttach")
        api_data = api_data.get('data', {}).get('videoPlayRes', "")
        live_data = json.loads(api_data).get('liveAdaptiveManifest', [])[0]
        self.representation = live_data.get('adaptationSet', {}).get('representation', {})

    @property
    def title(self):
        if self.is_open is False:
            return "当前主播未开播"
        return self.raw_data.get("caption")

    @property
    def start_time(self):
        if self.is_open is False:
            return "????????"
        create_time = self.raw_data.get('liveStartTime', 0) // 1000
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(create_time))

    def m3u8_url(self, quality: [int, str] = -1, only_url: bool = True):
        assert self.is_open is True
        if quality == -1:
            for x in self.representation:
                if x['defaultSelect'] is True:
                    if only_url is True:
                        return x['url']
                    return x
        elif quality in range(len(self.representation)):
            if only_url is True:
                return self.representation[quality]['url']
            return self.representation[quality]

    def play(self, potplayer_path: [os.PathLike, str], quality: [int, str] = -1):
        assert self.is_open is True
        assert os.path.exists(potplayer_path)
        adapt = self.m3u8_url(quality, False)
        player_title = f'"{self.start_time}|{self.parent}{self.title}-{adapt["name"]}"'.replace(" ", '')
        cmds = [potplayer_path, adapt['url'], "/title", emoji_cleanup(player_title)]
        return subprocess.Popen(cmds, stdout=subprocess.PIPE)


class AcLiveUp:
    uid = None
    is_404 = False
    raw_data = dict()
    report_data = dict()
    live = None

    def __init__(self, acer, uid: [int, str]):
        self.acer = acer
        self.uid = uid
        self.AcUp = self.acer.acfun.AcUp(self.uid)
        self.is_404 = self.AcUp.is_404
        self.loading()
        self._saver = None
        if hasattr(self.acer, 'acsaver'):
            self._saver = acer.acsaver.get_saver(self)

    @property
    def referer(self):
        return f"{AcSource.routes['live']}{self.uid}"

    @property
    def qrcode(self):
        parma = {
            "content": self.referer,
            "contentType": "URL",
            "toShortUrl": False,
            "width": 100,
            "height": 100
        }
        return f"{AcSource.apis['qrcode']}?{parse.urlencode(parma)}"

    @property
    def mobile_url(self):
        return f"{AcSource.routes['share_live']}{self.uid}"

    @property
    def mobile_qrcode(self):
        parma = {
            "content": self.mobile_url,
            "contentType": "URL",
            "toShortUrl": False,
            "width": 100,
            "height": 100
        }
        return f"{AcSource.apis['qrcode']}?{parse.urlencode(parma)}"

    @property
    def title(self):
        if self.past_time < 0:
            return "未开播"
        return self.raw_data.get('title', '')

    @property
    def cover(self):
        urls = self.raw_data.get("coverUrls", [])
        if len(urls):
            return urls[0]
        return None

    @property
    def username(self):
        return self.raw_data.get('user', {}).get('name', '')

    def up(self):
        return self.acer.acfun.AcUp(self.uid)

    def __repr__(self):
        return f"AcLive(#{self.uid} {self.title} @{self.username})".encode(errors='replace').decode()

    def loading(self):
        param = {"authorId": self.uid}
        api_req = self.acer.client.get(AcSource.apis['live_info'], params=param)
        self.raw_data = api_req.json()
        if self.past_time > -1:
            self.live = LiveItem(self.acer, self.uid, self)
        if self.acer.is_logined:
            self.report_data['host'] = self._get_report_data('liveStream')
            self.report_data['audience'] = self._get_report_data('liveStreamAudience')

    def save_all(self):
        if self._saver is None:
            raise ImportError("Depend on acsaver>=0.1.3, and need setup 'acsaver_path' in acer first")
        return self._saver.save_all()

    @property
    def past_time(self):
        if "createTime" not in self.raw_data:
            return -1
        return (time.time_ns() // pow(10, 6)) - self.raw_data.get("createTime", 0)

    def contents(self, obj: bool = False):
        param = {"authorId": self.uid}
        api_req = self.acer.client.get(AcSource.apis['live_up_contents'], params=param)
        api_data = api_req.json()
        if obj is False:
            return api_data
        return [self.acer.acfun.AcVideo(i.get('dougaId')) for i in api_data.get('contributeList', {}).get('feed', [])]

    def _api_action(self, api_name: str, form_data: dict):
        param = {
            "subBiz": "mainApp",
            "kpn": "ACFUN_APP",
            "kpf": "PC_WEB",
            "userId": self.acer.uid,
            "did": self.acer.did,
        }
        param = self.acer.update_token(param)
        api_req = self.acer.client.post(AcSource.apis[api_name], params=param, data=form_data,
                                        headers={'referer': f"{AcSource.routes['live_index']}"})
        return api_req.json()

    def my_balance(self):
        api_data = self._api_action('live_balance', {"visitorId": self.uid})
        values = api_data.get("data", {}).get("payWalletTypeToBalance", {})
        return {"acb": values.get('1', 0), "banana": values.get('2', 0)}

    def medal_info(self):
        api_req = self.acer.client.post(AcSource.apis['live_medal'], params={"uperId": self.uid})
        api_data = api_req.json()
        assert api_data.get("result") == 0
        return api_data

    def push_danmaku(self, content: str):
        if self.live.is_open is False:
            return False
        form_data = {
            "visitorId": self.uid,
            "liveId": self.live.liveId,
            "content": content
        }
        api_data = self._api_action('live_danmaku', form_data)
        return api_data.get('result') == 1

    def like(self, times: int, max_retry: int = 10):
        if self.live.is_open is False:
            return False
        form_data = {
            "visitorId": self.uid,
            "liveId": self.live.liveId,
            "count": 1,
            "durationMs": 800
        }
        retry = 0
        while times > 0 and retry <= max_retry:
            api_data = self._api_action('live_like', form_data)
            if api_data.get('result') == 1 and api_data.get('data', {}).get('count') == 1:
                times -= 1
            else:
                retry += 1
            time.sleep(1)
        return True

    def gift_list(self):
        if self.live.is_open is False:
            return False
        form_data = {
            "visitorId": self.uid,
            "liveId": self.live.liveId,
        }
        api_data = self._api_action('live_gift_list', form_data)
        gifts = dict()
        for gift in api_data.get('data', {}).get('giftList', []):
            gifts.update({f"{gift['giftId']}": gift})
        ext_gift = api_data.get('data', {}).get('externalDisplayGift', {}).get('giftList', [])
        if len(ext_gift):
            ext_gift = ext_gift[0]
            ext_gift.update({"tipsDelayTime": api_data.get('data', {}).get('externalDisplayGiftTipsDelayTime', 0)})
            gifts.update({f"{ext_gift['giftId']}": ext_gift})
        return gifts

    def send_gift(self, gift_id: int, size: int, times: int = 1, max_retry: int = 10):
        if self.live.is_open is False:
            return False
        gift_data = self.gift_list()
        # 判断礼物类型是否存在
        if f"{gift_id}" not in gift_data:
            return False
        this_gift = gift_data.get(f"{gift_id}", {})
        # 判断礼物数量是否正确
        if size not in this_gift.get("allowBatchSendSizeList", []):
            return False
        # 判断余额是否充足
        gift_type = this_gift.get("payWalletType", 0)
        gift_type_name = [0, 'acb', 'banana'][gift_type]
        gift_price = this_gift.get("giftPrice")
        total_price = gift_price * size * times
        balance = self.my_balance()
        if balance[gift_type_name] < total_price:
            return False
        combo_id = f"{gift_id}_{gift_id}_{time.time():.0f}000"
        form_data = {
            "visitorId": self.uid,
            "liveId": self.live.liveId,
            "giftId": gift_id,
            "batchSize": size,
            "comboKey": combo_id
        }
        retry = 0
        while times > 0 and retry <= max_retry:
            api_data = self._api_action('live_send_gift', form_data)
            if api_data.get('result') == 1:
                times -= 1
            else:
                retry += 1
            time.sleep(0.1)
        return True

    @need_login
    def _get_report_data(self, sub_biz: str):
        assert sub_biz in ['liveStream', 'liveStreamAudience']
        api_name = {
            'liveStream': "live_report_h0",
            'liveStreamAudience': "live_report_a0"
        }
        data = {
            "subBiz": sub_biz,
            "kpn": "ACFUN_APP",
            "kpf": "PC_WEB",
            "appver": "1.0.0",
            "userId": self.acer.uid,
            "did": self.acer.did,
        }
        data = self.acer.update_token(data)
        api_req = self.acer.client.post(AcSource.apis[api_name[sub_biz]], params=data, json=data)
        api_data = api_req.json()
        assert api_data.get("result") == 1
        config = json.loads(api_data.get('json'))
        options = list()
        for x in config['config']['props']['children']:
            text = x['label']
            key = x['output']
            option_id = api_data['reportCodeMap'][key]
            options.append({'id': option_id, 'key': key, 'text': text})
        return options

    def _report_req(self, sub_biz: str, code: int, reason: [str, None] = None):
        api_name = {
            'liveStream': "live_report_h1",
            'liveStreamAudience': "live_report_a1"
        }
        data = {
            "reportCode": code,
            "reportedObject": f"{self.uid}",
            "extra": "{\"report_time\":" + str(self.past_time) + "}"
        }
        if isinstance(reason, str):
            data['reportReason'] = {"reason": reason}
        param = {
            "subBiz": sub_biz,
            "kpn": "ACFUN_APP",
            "kpf": "PC_WEB",
            "appver": "1.0.0",
            "userId": self.acer.uid,
            "did": self.acer.did,
        }
        api_req = self.acer.client.post(AcSource.apis[api_name[sub_biz]], params=param, json=data)
        api_data = api_req.json()
        return api_data

    @need_login
    def report_host(self, code: int, reason: [str, None] = None):
        codes = [i['id'] for i in self.report_data['host']]
        assert code in codes
        return self._report_req('liveStream', code, reason)

    @need_login
    def report_audience(self, code: int, reason: [str, None] = None):
        codes = [i['id'] for i in self.report_data['audience']]
        assert code in codes
        return self._report_req('liveStreamAudience', code, reason)
