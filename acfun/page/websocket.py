# coding=utf-8
import json
import arrow
import time
import random
import base64
import asyncio
import threading
import websocket, ssl
from acfun.source import routes, apis, websocket_links, header
from acfun.protos import AcProtos

__author__ = 'dolacmeo'

# https://github.com/wpscott/AcFunDanmaku/blob/master/AcFunDanmu/README.md
# https://github.com/wpscott/AcFunDanmaku/blob/master/AcFunDanmu/data.md
# https://github.com/orzogc/acfundanmu/blob/master/proto.go
# https://developers.google.com/protocol-buffers/docs/pythontutorial
# https://websocket-client.readthedocs.io/en/latest/getting_started.html

# https://protogen.marcgravell.com/decode

# websocket 异步线程 同步化 + 背景进程
# https://stackoverflow.com/questions/51197063/python-websockets-in-synchronous-program
# 构建多线程异步 websocket
# 在同步返回结果前存留seqId为标识的线程
# 根据异步返回结果匹配seqId线程，并将结果返回给等待中的线程，异步变为同步
# 主要进程如下，需要线程守护：
# 1.背景线程持续接收服务器返回信息
# 2.keep alive 保持长连接
# 3.等待接收新的指令
# 进程初始需要执行初始化：注册
# 将注册后一系列过程同步，并保持必要信息


def uint8_payload_to_base64(data: dict):
    """
    用于反解网页中等待encode的payload
    进入页面: https://message.acfun.cn/im
    调试js  : https://static.yximgs.com/udata/pkg/acfun-im/ImSdk.b0aeed.js
    设置断点: 9145 => e.payloadData
    return: base64encoded ==> https://protogen.marcgravell.com/decode
    """
    b_str = b''
    for x in range(len(data.keys())):
        b_str += bytes([data[str(x)]])
    return base64.standard_b64encode(b_str)


class AcWsConfig:
    did = None
    userId = None
    ssecurity = None
    sessKey = None
    visitor_st = None
    api_st = None
    api_at = None
    appId = 0
    instanceId = 0

    def __init__(self, acer):
        self.acer = acer
        self._get_token()

    def _get_did(self):
        live_page_req = self.acer.client.get(routes['live_index'])
        assert live_page_req.status_code // 100 == 2
        self.did = live_page_req.cookies.get('_did')

    def _get_token(self):
        self._get_did()
        if self.acer.is_logined:
            api_req = self.acer.client.post(apis['token'], data={"sid": "acfun.midground.api"})
            api_data = api_req.json()
            assert api_data.get('result') == 0
            self.ssecurity = api_data.get("ssecurity", '')
            self.api_st = api_data.get("acfun.midground.api_st", '').encode()
            self.api_at = api_data.get("acfun.midground.api.at", '').encode()
        else:
            api_req = self.acer.client.post(apis['token_visitor'], data={"sid": "acfun.api.visitor"})
            api_data = api_req.json()
            assert api_data.get('result') == 0
            self.ssecurity = api_data.get("acSecurity", '')
            self.visitor_st = api_data.get("acfun.api.visitor_st", '').encode()
        self.userId = api_data.get("userId")


class AcWebSocket:
    ws_link = None
    config = None
    _main_thread = None
    _tasks = dict()
    _commands = dict()
    _unread = []
    is_register_done = False

    def __init__(self, acer):
        self.acer = acer
        # websocket.enableTrace(True)
        self.ws_link = random.choice(websocket_links)
        self.config = AcWsConfig(self.acer)
        self.protos = AcProtos(self)
        self.ws = websocket.WebSocketApp(
            url=self.ws_link,
            on_open=self.register,
            on_message=self.message,
            on_error=self.on_error,
            on_close=self.on_close,
            on_ping=self.keep_alive_request,
            on_pong=self.keep_alive_response,
        )
        self.listenner = dict()

    def run(self):
        def _run():
            self.ws.run_forever(
                # sslopt={"cert_reqs": ssl.CERT_NONE},
                ping_interval=30, ping_timeout=10,
                skip_utf8_validation=True,
                origin="live.acfun.cn",
            )
        self._main_thread = threading.Thread(target=_run)
        self._main_thread.start()
        return self

    def add_task(self, seqId: int, command, content):
        if f"{seqId}" not in self._tasks:
            self._tasks[f"{seqId}"] = dict()
        self._tasks[f"{seqId}"]["send"] = {"command": command, "content": content, "time": time.time()}
        if command not in self._commands:
            self._commands[command] = []
        self._commands[command].append({"seqId": f"{seqId}", "way": "send", "time": time.time()})
        # print("send: ", base64.standard_b64encode(content))
        self.ws.send(content)

    def task(self, seqId: int, command, content):
        self.add_task(seqId, command, content)
        if f"{seqId}" not in self.listenner:
            self.listenner[f"{seqId}"] = None

    def anser_task(self, seqId: int, command, result):
        if f"{seqId}" not in self._tasks:
            self._tasks[f"{seqId}"] = {}
        self._tasks[f"{seqId}"]["recv"] = {"command": command, "content": result, "time": time.time()}
        if command not in self._commands:
            self._commands[command] = []
        self._commands[command].append({"seqId": f"{seqId}", "way": "recv", "time": time.time()})
        if f"{seqId}" in self.listenner:
            self.listenner[f"{seqId}"] = result
        self._unread.append(f"{seqId}.recv")

    def register(self, ws):
        self.task(*self.protos.Basic_Register_Request())

    def message(self, ws, message):
        # print("recv: ", base64.standard_b64encode(message))
        self.anser_task(*self.protos.decode(message))

    def keep_alive_request(self, ws, message):
        self.add_task(*self.protos.Basic_ping())

    def keep_alive_response(self, ws, message):
        self.add_task(*self.protos.Keep_Alive_Request())

    def on_close(self, ws):
        if self._main_thread.is_alive():
            self.ws.close()
        print(">>>>>>AcWebsocket CLOSED<<<<<<<")

    def on_error(self, ws, e):
        print("error: ", e)
        pass

    def im_session(self):
        return self.task(*self.protos.Message_Session())

    def im_pull_message(self, uid: int, minSeq: int, maxSeq: int, count: int = 10):
        payload = self.protos.Message_PullOld_Request(uid, minSeq, maxSeq, count)
        return self.task(*payload)

    def im_send(self, uid: int, content: str):
        payload = self.protos.Message_Request(uid, content)
        return self.task(*payload)
