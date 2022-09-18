# coding=utf-8
import os
import time
import json
import subprocess
from acfunsdk.source import scheme, domains, routes, apis

__author__ = 'dolacmeo'


class AcLive:
    last_update = None
    raw_data = dict()

    def __init__(self, acer):
        self.acer = acer
        self._get_list()

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

    def __init__(self, acer, uid: [int, str], raw: [dict, None] = None):
        self.acer = acer
        self.uid = uid
        self.raw = raw
        if self.raw is None:
            self.infos()
        self.AcUp = self.acer.acfun.AcUp(self.uid)
        self.media_data = self.media_list()
        self.is_404 = self.AcUp.is_404

    @property
    def title(self):
        return self.raw.get('title', '')

    @property
    def username(self):
        return self.raw.get('user', {}).get('name', '')

    def up(self):
        return self.acer.acfun.AcUp(self.uid)

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
            "userId": self.acer.uid,
            "did": self.acer.client.cookies.get('_did'),
        }
        param = self.acer.update_token(param)
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

    # def record(self, save_path: [str, os.PathLike], quality: int = 1):
    #     live_adapt = self.media_list()
    #     if live_adapt is False:
    #         return False
    #     if quality not in range(len(live_adapt)):
    #         quality = 1
    #     now_time = time.strftime('%Y%m%dT%H%M%S', time.localtime(time.time()))
    #     live_obs_stream = live_adapt[quality]['url']
    #     stream_split = parse.urlsplit(live_obs_stream)
    #     stream_key = parse.parse_qs(stream_split.query).get('auth_key', [])[0]
    #     live_obs_stream = f"{stream_split.scheme}://{stream_split.netloc}{stream_split.path}?auth_key={stream_key}"
    #     if os.path.exists(save_path) is True:
    #         if os.path.isdir(save_path) is True:
    #             save_path = os.path.join(save_path, f"AcLive({self.uid})@{now_time}.mp4")
    #         elif os.path.isfile(save_path) is True:
    #             print(f"save_path is exist! {save_path}")
    #             return False
    #     else:
    #         if os.path.isdir(save_path) is True:
    #             print(f"save_path is not exist! {save_path}")
    #             return False
    #     if not save_path.endswith('.mp4'):
    #         save_path += ".mp4"
    #     ffmpeg = get_usable_ffmpeg()
    #     if ffmpeg is None:
    #         print(f"record need ffmpeg")
    #         return False
    #     cmd_with_progress = [
    #         ffmpeg,
    #         "-progress", "-", "-nostats",
    #         '-loglevel', '+repeat',
    #         "-i", f"{live_obs_stream}",
    #         "-c:v", "copy", "-c:a", "copy",
    #         f"{save_path}"
    #     ]
    #     p = subprocess.Popen(
    #         cmd_with_progress,
    #         stdin=subprocess.PIPE,
    #         stdout=subprocess.PIPE,
    #         stderr=subprocess.STDOUT,
    #         universal_newlines=False)
    #     begin_read = False
    #     tmp = dict()
    #     console = Console()
    #
    #     def display_tui(data):
    #         filesize = int(data.get('total_size', 0))
    #         infos = f" 已录制 {data.get('out_time', '00:00:00.000000')}\r\n " \
    #                 f" 比特率: {data.get('bitrate', '???')}   " \
    #                 f"大小: {sizeof_fmt(filesize): >6} "
    #         record_panel = Panel(Text(infos, justify='center'),
    #                              title=f"AcLive({self.uid})@{now_time}.mp4",
    #                              border_style='red', width=50, style="black on white")
    #         return record_panel
    #
    #     with Live(console=console) as live:
    #         while True:
    #             if p.stdout is None:
    #                 continue
    #             stderr_line = p.stdout.readline().decode("utf-8", errors="replace").strip()
    #             if stderr_line == "" and p.poll() is not None:
    #                 break
    #             if stderr_line == "Press [q] to stop, [?] for help":
    #                 begin_read = True
    #                 continue
    #             if begin_read is True:
    #                 r = stderr_line.split('=')
    #                 tmp.update({r[0]: r[1]})
    #                 live.update(Align.center(display_tui(tmp)))
    #
    #     return True

