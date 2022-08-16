# coding=utf-8
import os
import time
import json
import js2py
import pyperclip
import subprocess
from bs4 import BeautifulSoup as Bs
from source import scheme, domains, routes, apis

__author__ = 'dolacmeo'


class AcLive:
    last_update = None
    raw_data = dict()

    def __init__(self, acer):
        self.acer = acer
        self._get_list()

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

    def __init__(self, acer, uid: [int, str], raw: [dict, None] = None):
        self.acer = acer
        self.uid = uid
        self.raw = raw
        if self.raw is None:
            self.infos()

    @property
    def title(self):
        return self.raw.get('title', '')

    @property
    def username(self):
        return self.raw.get('user', {}).get('name', '')

    def __repr__(self):
        return f"AcLive(#{self.uid} {self.title} @{self.username})"

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

    def media_list(self):
        param = {
            "subBiz": "mainApp",
            "kpn": "ACFUN_APP",
            "kpf": "PC_WEB",
            "userId": self.acer.uid,
            "did": self.acer.client.cookies.get('_did'),
            "acfun.midground.api_st": self.acer.token.get('acfun.midground.api_st', "")
        }
        form_data = {"authorId": self.uid, "pullStreamType": "FLV"}
        api_req = self.acer.client.post(apis['live_play'], params=param, data=form_data,
                                        headers={'referer': f"{scheme}://{domains['live']}/"})
        api_data = api_req.json()
        if api_data.get('result') != 1:
            print(api_data)
            return False
        api_data = api_data.get('data', {}).get('videoPlayRes', "")
        live_data = json.loads(api_data).get('liveAdaptiveManifest', [])[0]
        live_adapt = live_data.get('adaptationSet', {}).get('representation', {})
        return live_adapt

    def playing(self, level: int = 1, potplayer: [str, None] = None):
        live_adapt = self.media_list()
        if live_adapt is False:
            return False
        if level not in range(len(live_adapt)):
            level = 1
        create_time = self.raw.get('createTime', 0) // 1000
        start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(create_time))
        live_title = " ".join([str(self), live_adapt[level]['name'], f"🎬 {start_time}"])
        live_obs_stream = live_adapt[level]['url']
        if potplayer is not None and os.path.exists(potplayer):
            print(f"[{potplayer}] 开始播放...... \n{live_title}")
            subprocess.Popen([potplayer, live_obs_stream, "/title", f'"{live_title}"'], stdout=subprocess.PIPE)
        else:
            print(f"未设置PotPlayer 已复制串流地址 请自行播放")
            pyperclip.copy(live_obs_stream)
        return live_obs_stream

