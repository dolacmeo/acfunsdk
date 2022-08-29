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


class AcWsConfig:
    did = None
    userId = None
    acSecurity = None
    ssecurity = None
    visitor_st = None
    api_st = None
    api_at = None

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
            self.acSecurity = api_data.get("acSecurity", '')
            self.visitor_st = api_data.get("acfun.api.visitor_st", '').encode()
        self.userId = api_data.get("userId")
        print(self.userId)


class AcWebSocket:
    ws_link = None
    config = None

    def __init__(self, acer):
        self.acer = acer
        self.ws_link = random.choice(websocket_links)
        print(self.ws_link)
        self.config = AcWsConfig(self.acer)
        self.protos = AcProtos(self.config)
        # self.ws_key = base64.standard_b64encode(bytes([random.randint(0, 255) for _ in range(16)]))
        hh = {
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Cache-Control": "no-cache",
            "Connection": "Upgrade",
            "Origin": "https://live.acfun.cn",
            "Pragma": "no-cache",
            # "Sec-WebSocket-Extensions": "permessage-deflate; client_max_window_bits",
            # "Sec-WebSocket-Version": "13",
            "Upgrade": "websocket",
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/104.0.5112.102 Safari/537.36'
        }
        hh.update({"Origin": "https://live.acfun.cn"})
        self.ws = websocket.WebSocketApp(
            url=self.ws_link,
            header=hh,
            on_open=self._register,
            on_message=self._message,
            on_error=self._error,
            # on_close=self._close,
            # on_ping=self._ping,
            # on_pong=self._pong,
        )
        self.ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
        pass

    def _register(self, ws):
        basic_register = self.protos.Basic_Register()
        print("send: ", base64.standard_b64encode(basic_register))
        self.ws.send(basic_register)
        self.protos.SeqId += 1

    def _message(self, ws, message):
        print("recv: ", base64.standard_b64encode(message))
        self.protos.receive(message)

    def _close(self, ws):
        pass

    def _error(self, ws):
        # print(e)
        # print("error", e)
        pass
