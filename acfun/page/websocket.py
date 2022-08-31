# coding=utf-8
import time
import random
import base64
import asyncio
import threading
import websocket
from acfun.source import routes, apis, websocket_links
from acfun.protos.Im import AcImProtos

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
    进入页面: https://live.acfun.cn/live/
    设置断点: 9145  => e.payloadData
    调试js  : https://ali-imgs.acfun.cn/kos/nlav10360/static/js/3.867c7c46.js
    设置断点: 40910 => t
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
    tasks = dict()
    commands = dict()
    unread = []
    is_register_done = False

    def __init__(self, acer):
        self.acer = acer
        # websocket.enableTrace(True)
        self.ws_link = random.choice(websocket_links)
        self.config = AcWsConfig(self.acer)
        self.im_protos = AcImProtos(self)
        self.ws = websocket.WebSocketApp(
            url=self.ws_link,
            on_open=self._register,
            on_message=self._message,
            on_error=self._on_error,
            on_close=self._on_close,
            on_ping=self._keep_alive_request,
            on_pong=self._keep_alive_response,
        )
        self.listenner = dict()

    def run(self):
        def _run():
            self.ws.run_forever(
                ping_interval=30, ping_timeout=10,
                skip_utf8_validation=True,
                origin="live.acfun.cn",
            )
        self._main_thread = threading.Thread(target=_run)
        self._main_thread.start()
        return self

    def add_task(self, seqId: int, command, content):
        if f"{seqId}" not in self.tasks:
            self.tasks[f"{seqId}"] = dict()
        self.tasks[f"{seqId}"]["send"] = {"command": command, "content": content, "time": time.time()}
        if command not in self.commands:
            self.commands[command] = []
        self.commands[command].append({"seqId": f"{seqId}", "way": "send", "time": time.time()})
        self.ws.send(content)

    def task(self, seqId: int, command, content):
        self.add_task(seqId, command, content)
        # if f"{seqId}" not in self.listenner:
        #     self.listenner[f"{seqId}"] = None

    def ans_task(self, seqId: int, command, result):
        if f"{seqId}" not in self.tasks:
            self.tasks[f"{seqId}"] = {}
        self.tasks[f"{seqId}"]["recv"] = {"command": command, "content": result, "time": time.time()}
        if command not in self.commands:
            self.commands[command] = []
        self.commands[command].append({"seqId": f"{seqId}", "way": "recv", "time": time.time()})
        # if f"{seqId}" in self.listenner:
        #     self.listenner[f"{seqId}"] = result
        self.unread.append(f"{seqId}.recv")
        if command == 'Basic.Register':
            self.task(*self.im_protos.ClientConfigGet_Request())
            print(f"did       : {self.config.did}")
            print(f"userId    : {self.config.userId}")
            print(f"ssecurity : {self.config.ssecurity}")
            print(f"sessKey   : {self.config.sessKey.decode()}")
            self.is_register_done = True
            print(">>>>>>>> AcWebsocket Registed<<<<<<<<<")
        elif command == 'Basic.ClientConfigGet':
            self.task(*self.im_protos.KeepAlive_Request())
            self.im_protos.client_config = result
            print(">>>>>>>> AcWebsocket  Ready  <<<<<<<<<")

    def _register(self, ws):
        print(">>>>>>> AcWebsocket Connecting<<<<<<<<")
        self.task(*self.im_protos.BasicRegister_Request())

    def _message(self, ws, message):
        self.ans_task(*self.im_protos.decode(message))

    def _keep_alive_request(self, ws, message):
        self.add_task(*self.im_protos.BasicPing_Request())

    def _keep_alive_response(self, ws, message):
        if self.is_register_done:
            self.add_task(*self.im_protos.KeepAlive_Request())

    def _on_close(self, ws, close_status_code, close_msg):
        # Because on_close was triggered, we know the opcode = 8
        if close_status_code or close_msg:
            print("on_close args:")
            print(f"  close status code: {close_status_code}")
            print(f"  close message    : {close_msg}")
        print(">>>>>>>> AcWebsocket  CLOSED <<<<<<<<<")

    def _on_error(self, ws, e):
        print("error: ", e)
        self.close()

    def close(self):
        self.ws.close()

    def im_get_sessions(self):
        message = self.im_protos.MessageSession_Request()
        return self.task(*message)

    def im_session_start(self, uid: int):
        message = self.im_protos.SessionCreate_Request(uid)
        return self.task(*message)

    def im_session_close(self, uid: int):
        message = self.im_protos.SessionRemove_Request(uid)
        return self.task(*message)

    def im_pull_message(self, uid: int, minSeq: int, maxSeq: int, count: int = 10):
        message = self.im_protos.MessagePullOld_Request(uid, minSeq, maxSeq, count)
        return self.task(*message)

    def im_send(self, uid: int, content: str):
        message = self.im_protos.MessageContent_Request(uid, content)
        return self.task(*message)

    def im_send_image(self, uid: int, image_data: bytes):
        message = self.im_protos.MessageImage_Request(uid, image_data)
        return self.task(*message)
