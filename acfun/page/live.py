# coding=utf-8
import os
import time
import json
import pyperclip
import subprocess
from acfun.source import scheme, domains, routes, apis
from acfun.page.websocket import AcWebSocket

__author__ = 'dolacmeo'


class AcLive:
    last_update = None
    raw_data = dict()

    def __init__(self, acer):
        self.acer = acer
        self._get_list()

    def login(self):
        index_req = self.acer.client.get(routes['live_index'])
        _did = index_req.cookies.get('_did')
        if self.acer.is_logined:
            token_req = self.acer.client.post(apis['token'], data={'sid': "acfun.midground.api"})
            token = token_req.json()
        else:
            token_req = self.acer.client.post(apis['token_visitor'], data={'sid': "acfun.api.visitor"})
            token = token_req.json()
        print(token)

    def _get_list(self):
        if self.last_update is None or time.time() - self.last_update >= 60:
            api_req = self.acer.client.get(apis['live_list'])
            self.raw_data = api_req.json()
            self.last_update = time.time()

    def list(self):
        self._get_list()
        lives = list()
        for x in self.raw_data.get('liveList', []):
            lives.append(LiveUp(self.acer, x.get('authorId'), x))
        return lives

    def get(self, uid: [int, str]):
        return LiveUp(self.acer, uid)


class LiveUp:
    uid = None
    raw = None
    acws = None

    def __init__(self, acer, uid: [int, str], raw: [dict, None] = None):
        self.acer = acer
        self.uid = uid
        self.raw = raw
        if self.raw is None:
            self.infos()
        self.AcUp = self.acer.AcUp({"userId": self.uid})

    @property
    def title(self):
        return self.raw.get('title', '')

    @property
    def username(self):
        return self.raw.get('user', {}).get('name', '')

    def __repr__(self):
        return f"AcLive(#{self.uid} {self.title} @{self.username})".encode(errors='replace').decode()

    def infos(self, key: [str, None] = None):
        param = {"authorId": self.uid}
        api_req = self.acer.client.get(apis['live_info'], params=param)
        self.raw = api_req.json()
        if key is not None:
            return self.raw.get(key)
        return self.raw

    def contents(self):
        param = {"authorId": self.uid}
        api_req = self.acer.client.get(apis['live_up_contents'], params=param)
        api_data = api_req.json()
        return [self.acer.AcVideo(i.get('dougaId')) for i in api_data.get('contributeList', {}).get('feed', [])]

    def _api_action(self, api_name: str, form_data: dict):
        param = {
            "subBiz": "mainApp",
            "kpn": "ACFUN_APP",
            "kpf": "PC_WEB",
            "userId": self.acer.uid,
            "did": self.acer.client.cookies.get('_did'),
            "acfun.midground.api_st": self.acer.token.get('acfun.midground.api_st', "")
        }
        api_req = self.acer.client.post(apis[api_name], params=param, data=form_data,
                                        headers={'referer': f"{scheme}://{domains['live']}/"})
        return api_req.json()

    def my_balance(self):
        api_data = self._api_action('live_balance', {"visitorId": self.uid})
        values = api_data.get("data", {}).get("payWalletTypeToBalance", {})
        return {"acb": values.get('1', 0), "banana": values.get('2', 0)}

    def media_list(self):
        form_data = {"authorId": self.uid, "pullStreamType": "FLV"}
        api_data = self._api_action('live_play', form_data)
        if api_data.get('result') != 1:
            return False
        api_data = api_data.get('data', {}).get('videoPlayRes', "")
        live_data = json.loads(api_data).get('liveAdaptiveManifest', [])[0]
        live_adapt = live_data.get('adaptationSet', {}).get('representation', {})
        return live_adapt

    def push_danmaku(self, content: str):
        form_data = {
            "visitorId": self.uid,
            "liveId": self.raw.get("liveId"),
            "content": content
        }
        api_data = self._api_action('live_danmaku', form_data)
        return api_data.get('result') == 1

    def like(self, times: int, max_retry: int = 10):
        form_data = {
            "visitorId": self.uid,
            "liveId": self.raw.get("liveId"),
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
        form_data = {
            "visitorId": self.uid,
            "liveId": self.raw.get("liveId"),
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
            "liveId": self.raw.get("liveId"),
            "giftId": gift_id,
            "batchSize": size,
            "comboKey": combo_id
        }
        retry = 0
        while times > 0 and retry <= max_retry:
            api_data = self._api_action('live_send_gift', form_data)
            print(api_data)
            if api_data.get('result') == 1:
                times -= 1
            else:
                retry += 1
            time.sleep(0.1)
        return True

    def playing(self, potplayer: [str, None] = None, quality: int = 1):
        live_adapt = self.media_list()
        if live_adapt is False:
            return False
        if quality not in range(len(live_adapt)):
            quality = 1
        create_time = self.raw.get('createTime', 0) // 1000
        start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(create_time))
        live_title = " ".join([str(self), live_adapt[quality]['name'], f"🎬 {start_time}"])
        live_obs_stream = live_adapt[quality]['url']
        if potplayer is not None and os.path.exists(potplayer):
            print(f"[{potplayer}] 开始播放......\r\n {live_title}")
            subprocess.Popen([potplayer, live_obs_stream, "/title", f'"{live_title}"'], stdout=subprocess.PIPE)
        else:
            print(f"未设置PotPlayer 已复制串流地址 请自行播放")
            pyperclip.copy(live_obs_stream)
        return live_obs_stream

    def watching_danmaku(self, room_bans: [list, None] = None, potplayer: [str, None] = None, quality: int = 1):
        # 传参举例
        # bans = [
        #     # "ZtLiveScActionSignal",
        #     "ZtLiveScStateSignal",
        #     "ZtLiveScNotifySignal",
        #     "ZtLiveScStatusChanged",
        #     "ZtLiveScTicketInvalid",
        # ]
        # player = [r"C:\Program Files\PotPlayer64\PotPlayerMini64.exe", 2]
        # self.watching_danmaku(bans, *player)
        self.acws = AcWebSocket(self.acer)
        self.acws.run()
        self.acws.wait4ready()
        self.acws.live_enter_room(self.uid, room_bans, potplayer, quality)
        try:
            count = 0
            while True:
                count += 1
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.acws.close()

