# coding=utf-8
import os
import time
import json
import subprocess
from acfunsdk.source import scheme, domains, routes, apis
from acfunsdk.exceptions import need_login

__author__ = 'dolacmeo'


class AcLive:
    last_update = None
    raw_data = dict()

    def __init__(self, acer):
        self.acer = acer
        self._get_list()

    @property
    def referer(self):
        return f"{routes['live_index']}"

    def __repr__(self):
        return f"AcLive(直播 - AcFun弹幕视频网)"

    def _get_list(self):
        if self.last_update is None or time.time() - self.last_update >= 60:
            api_req = self.acer.client.get(apis['live_list'])
            self.raw_data = api_req.json()
            self.last_update = time.time()

    def list(self):
        self._get_list()
        lives = list()
        for x in self.raw_data.get('liveList', []):
            lives.append(AcLiveUp(self.acer, x.get('authorId'), x))
        return lives

    def get(self, uid: [int, str]):
        return AcLiveUp(self.acer, uid)


class AcLiveVisitor:
    client = None
    did = None
    uid = None
    is_logined = False
    tokens = dict()

    def __init__(self, acer):
        self.acer = acer
        self.is_logined = self.acer.is_logined
        self.client = self.acer.client
        self.loading()

    def loading(self):
        if self.is_logined is True:
            self.did = self.acer.did
            self.uid = self.acer.uid
            self.tokens = self.acer.tokens
        else:
            did_req = self.client.get(apis['app'])
            self.did = did_req.cookies.get('_did')
            token_req = self.client.post(apis['token_visitor'],
                                         data={"sid": "acfun.api.visitor"})
            token_data = token_req.json()
            self.uid = token_data.get("userId"),
            self.tokens = {
                "ssecurity": token_data.get("acSecurity", ''),
                "visitor_st": token_data.get("acfun.api.visitor_st", ''),
            }

    def update_token(self, data: dict):
        if self.is_logined:
            data.update({"acfun.midground.api_st": self.tokens['api_st']})
        else:
            data.update({"acfun.api.visitor_st": self.tokens['visitor_st']})
        return data


class AcLiveUp:
    uid = None
    raw = None
    acws = None
    is_open = False
    media_data = None
    is_404 = False
    liveId = None
    enterRoomAttach = None
    availableTickets = []
    report_data = dict()

    def __init__(self, acer, uid: [int, str], raw: [dict, None] = None):
        self.acer = acer
        self.uid = uid
        self.raw = raw
        if self.raw is None:
            self.infos()
        self.AcUp = self.acer.acfun.AcUp(self.uid)
        self.is_404 = self.AcUp.is_404
        self.visitor = AcLiveVisitor(self.acer)
        if self.visitor.is_logined:
            self.media_data = self.media_list()
            self.report_data['host'] = self._get_report_data('liveStream')
            self.report_data['audience'] = self._get_report_data('liveStreamAudience')

    @property
    def title(self):
        return self.raw.get('title', '')

    @property
    def username(self):
        return self.raw.get('user', {}).get('name', '')

    def up(self):
        return self.acer.acfun.AcUp(self.uid)

    @property
    def referer(self):
        return f"{routes['live']}{self.uid}"

    @property
    def past_time(self):
        p = (time.time_ns() // pow(10, 6)) - self.raw.get("createTime", 0)
        return p if p > 0 else -1

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
        return [self.acer.acfun.AcVideo(i.get('dougaId')) for i in api_data.get('contributeList', {}).get('feed', [])]

    def _api_action(self, api_name: str, form_data: dict):
        param = {
            "subBiz": "mainApp",
            "kpn": "ACFUN_APP",
            "kpf": "PC_WEB",
            "userId": self.visitor.uid,
            "did": self.visitor.did,
        }
        param = self.visitor.update_token(param)
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
        if api_data.get('result') == 129004:
            self.is_open = False
            return False
        elif api_data.get('result') != 1:
            return False
        self.is_open = True
        self.liveId = api_data['data'].get("liveId")
        self.availableTickets = api_data['data'].get("availableTickets", [])
        self.enterRoomAttach = api_data['data'].get("enterRoomAttach")
        api_data = api_data.get('data', {}).get('videoPlayRes', "")
        live_data = json.loads(api_data).get('liveAdaptiveManifest', [])[0]
        live_adapt = live_data.get('adaptationSet', {}).get('representation', {})
        return live_adapt

    def medal_info(self):
        api_req = self.acer.client.post(apis['live_medal'], params={"uperId": self.uid})
        api_data = api_req.json()
        assert api_data.get("result") == 0
        return api_data

    def push_danmaku(self, content: str):
        if self.is_open is False:
            return False
        form_data = {
            "visitorId": self.uid,
            "liveId": self.raw.get("liveId"),
            "content": content
        }
        api_data = self._api_action('live_danmaku', form_data)
        return api_data.get('result') == 1

    def like(self, times: int, max_retry: int = 10):
        if self.is_open is False:
            return False
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
        if self.is_open is False:
            return False
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
        if self.is_open is False:
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
            "liveId": self.raw.get("liveId"),
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
            print(f"未设置PotPlayer 请使用串流地址 请自行播放 \r\n {live_obs_stream}")
        return live_obs_stream

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
            "userId": self.visitor.uid,
            "did": self.visitor.did,
        }
        data = self.visitor.update_token(data)
        api_req = self.acer.client.post(apis[api_name[sub_biz]], params=data, json=data)
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
            "userId": self.visitor.uid,
            "did": self.visitor.did,
        }
        api_req = self.acer.client.post(apis[api_name[sub_biz]], params=param, json=data)
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
