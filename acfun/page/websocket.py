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

    def __init__(self, config: AcWsConfig):
        self.ws_link = random.choice(websocket_links)
        print(self.ws_link)
        self.config = config
        self.protos = AcProtos(self.config)
        self.ws = websocket.WebSocketApp(
            url=self.ws_link,
            header=header,
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
        print("reg req", base64.standard_b64encode(basic_register))
        self.ws.send(basic_register)
        self.protos.SeqId += 1

    def _message(self, ws, message):
        print(base64.standard_b64encode(message))
        self.protos.reveive(message)

    def _close(self, ws):
        pass

    def _error(self, ws):
        # print(e)
        # print("error", e)
        pass
