# coding=utf-8
import time
import random
import websocket, ssl
import base64
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

    def __init__(self, acer):
        self.acer = acer
        websocket.enableTrace(True)
        self.ws_link = random.choice(websocket_links)
        self.config = AcWsConfig(self.acer)
        self.ws = websocket.WebSocketApp(
            url=self.ws_link,
            on_open=self.register,
            on_message=self.message,
            on_error=self.error,
            on_close=self.close,
            on_ping=self.keep_alive_request,
            on_pong=self.keep_alive_response,
        )
        self.protos = AcProtos(self.config)

    def run(self):
        self.ws.run_forever(
            # sslopt={"cert_reqs": ssl.CERT_NONE},
            ping_interval=30, ping_timeout=10,
            skip_utf8_validation=True,
            origin="live.acfun.cn",
        )

    def register(self, ws):
        basic_register = self.protos.Basic_Register_Request()
        print("send: ", base64.standard_b64encode(basic_register))
        self.ws.send(basic_register)

    def message(self, ws, message):
        print("recv: ", base64.standard_b64encode(message))
        self.protos.decode(ws, message)

    def keep_alive_request(self, ws, message):
        ping = self.protos.Basic_ping()
        print("ping: ", base64.standard_b64encode(ping))
        self.ws.send(ping)

    def keep_alive_response(self, ws, message):
        keep_alive = self.protos.Keep_Alive_Request()
        print("ping: ", base64.standard_b64encode(keep_alive))
        self.ws.send(keep_alive)

    def close(self, ws):
        pass

    def error(self, ws):
        # print("error", e)
        pass
