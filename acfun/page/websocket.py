# coding=utf-8
import os
import json
import time
import arrow
import random
import base64
import asyncio
import threading
import websocket
import pyperclip
import subprocess
from acfun.source import routes, apis, websocket_links
from acfun.protos import AcProtos
from rich import print, console


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


def ac_live_room_reader(data: list, msg_bans: [list, None] = None):
    message_types = {
        "ZtLiveScActionSignal": "(粉丝互动)",
        "ZtLiveScStateSignal": "(数据更新)",
        "ZtLiveScNotifySignal": "(房管来啦)",
        "ZtLiveScStatusChanged": "(状态变更)",
        "ZtLiveScTicketInvalid": "(连接失效)[需要重连]",
    }
    msg_bans = [] if msg_bans is None else msg_bans
    signal_types = {
        "CommonActionSignalComment": "[送出弹幕]",
        "CommonActionSignalLike": "[爱心点赞]",
        "CommonActionSignalUserEnterRoom": "[进入房间]",
        "CommonActionSignalUserFollowAuthor": "[关注主播]",
        "AcfunActionSignalThrowBanana": "[投喂香蕉]",
        "CommonActionSignalGift": "[送出礼物]",
        "CommonActionSignalRichText": "[高级弹幕]",
        "AcfunActionSignalJoinClub": "[加守护团]",
        "AcfunStateSignalDisplayInfo": "[香蕉总数]",
        "CommonStateSignalDisplayInfo": "[在线人数][点赞数量]",
        "CommonStateSignalTopUsers": "[前三粉丝]",
        "CommonStateSignalRecentComment": "[近期弹幕]",
        "CommonStateSignalChatCall": "[连麦被叫呼叫]",
        "CommonStateSignalChatAccept": "[连麦被叫接受]",
        "CommonStateSignalChatReady": "[连麦被叫等待]",
        "CommonStateSignalChatEnd": "[连麦被叫结束]",
        "CommonStateSignalCurrentRedpackList": "[红包榜单]",
        "CommonStateSignalAuthorChatCall": "[连麦主叫呼叫]",
        "CommonStateSignalAuthorChatAccept": "[连麦主叫接受]",
        "CommonStateSignalAuthorChatReady": "[连麦主叫等待]",
        "CommonStateSignalAuthorChatEnd": "[连麦主叫结束]",
        "CommonStateSignalAuthorChatChangeSoundConfig": "[连麦主叫导播]",
        "CommonStateSignalPKAccept": "[连麦挑战接受]",
        "CommonStateSignalPKInvitation": "[连麦挑战邀请]",
        "CommonStateSignalPKReady": "[连麦挑战等待]",
        "CommonStateSignalPKSoundConfigChanged": "[连麦挑战导播]",
        "CommonStateSignalPkEnd": "[连麦挑战结束]",
        "CommonStateSignalPkStatistic": "[连麦挑战统计]",
        "CommonStateSignalWishSheetCurrentState": "[愿望列表状态]",
        "CommonNotifySignalKickedOut": "[踢出房间]",
        "CommonNotifySignalViolationAlert": "[违规警告]",
        "CommonNotifySignalLiveManagerState": "[房管状态]",
    }

    def user_info(payload_item):
        payload = payload_item['userInfo']
        base = f"<{payload['userId']}@{payload['nickname']}>"
        if 'badge' in payload:
            badge = json.loads(payload['badge']).get('medalInfo', {})
            base += f"『{badge['clubName']}|lv{badge['level']}』"
        return base

    messages = list()
    for item in data:
        signal_path = item['signal']
        if item['signal'].count(".") == 0:
            signal_path += "."
        msg_type, signal_name = signal_path.split(".")
        if msg_type in msg_bans:
            continue
        words = list()
        payload = item.get('payload')
        # 消息类型
        words.append(message_types.get(msg_type, "(????????)"))
        # 信号类型
        if signal_name:
            words.append(signal_types.get(signal_name, "[????????]"))
        # 内容信息
        if signal_name == "CommonActionSignalComment":
            words = list()
            for fans in payload:
                users = list()
                # 消息类型
                users.append(message_types.get(msg_type, "(????????)"))
                # 信号类型
                if signal_name:
                    users.append(signal_types.get(signal_name, "[????????]"))
                # 内容信息
                user = user_info(fans)
                content = fans['content']
                send_time = arrow.get(int(fans['sendTimeMs']), tzinfo="Asia/Shanghai").format("HH:mm:ss")
                users.append(f"{{{send_time}}} \r\n{user} 💬{content} \r\n")
                words.append("".join(users))
        elif signal_name == "CommonActionSignalLike":
            words = list()
            for fans in payload:
                users = list()
                # 消息类型
                users.append(message_types.get(msg_type, "(????????)"))
                # 信号类型
                if signal_name:
                    users.append(signal_types.get(signal_name, "[????????]"))
                # 内容信息
                user = user_info(fans)
                send_time = arrow.get(int(fans['sendTimeMs']), tzinfo="Asia/Shanghai").format("HH:mm:ss")
                users.append(f"{{{send_time}}}\r\n{user} 点赞了❤ \r\n")
                words.append("".join(users))
        elif signal_name == "CommonActionSignalUserEnterRoom":
            words = list()
            for newbee in payload:
                new_user = list()
                # 消息类型
                new_user.append(message_types.get(msg_type, "(????????)"))
                # 信号类型
                if signal_name:
                    new_user.append(signal_types.get(signal_name, "[????????]"))
                # 内容信息
                user = user_info(newbee)
                send_time = arrow.get(int(newbee['sendTimeMs']), tzinfo="Asia/Shanghai").format("HH:mm:ss")
                new_user.append(f"{{{send_time}}}\r\n{user} 进入直播间👤 \r\n")
                words.append("".join(new_user))
        elif signal_name == "CommonActionSignalUserFollowAuthor":
            user = user_info(payload)
            send_time = arrow.get(int(payload['sendTimeMs']), tzinfo="Asia/Shanghai").format("HH:mm:ss")
            words.append(f"{{{send_time}}}\r\n{user} 关注了主播👀 ")
        elif signal_name == "AcfunActionSignalThrowBanana":
            user = user_info(payload)
            send_time = arrow.get(int(payload['sendTimeMs']), tzinfo="Asia/Shanghai").format("HH:mm:ss")
            words.append(f"{{{send_time}}}{user}")
        elif signal_name == "CommonActionSignalGift":
            words = list()
            for fans in payload:
                users = list()
                # 消息类型
                users.append(message_types.get(msg_type, "(????????)"))
                # 信号类型
                if signal_name:
                    users.append(signal_types.get(signal_name, "[????????]"))
                # 内容信息
                user = user_info(fans)
                gift = f"送出{fans['batchSize']}个🎁[{fans['giftId']}]"
                if fans['comboCount'] > 1:
                    gift += f" 连击{fans['comboCount']}"
                send_time = arrow.get(int(fans['sendTimeMs']), tzinfo="Asia/Shanghai").format("HH:mm:ss")
                words.append(f"{{{send_time}}}\r\n{user} {gift} \r\n")
                words.append("".join(users))
        elif signal_name == "CommonActionSignalRichText":  # 高级弹幕
            pass
        elif signal_name == "AcfunActionSignalJoinClub":
            words = list()
            for fans in payload:
                users = list()
                # 消息类型
                users.append(message_types.get(msg_type, "(????????)"))
                # 信号类型
                if signal_name:
                    users.append(signal_types.get(signal_name, "[????????]"))
                # 内容信息
                user = user_info(fans)
                send_time = arrow.get(int(fans['sendTimeMs']), tzinfo="Asia/Shanghai").format("HH:mm:ss")
                words.append(f"{{{send_time}}} \r\n{user} 加入守护团 \r\n")
                words.append("".join(users))
        elif signal_name == "AcfunStateSignalDisplayInfo":
            words.append(f"🍌x{payload['bananaCount']}")
        elif signal_name == "CommonStateSignalDisplayInfo":
            if 'watchingCount' in payload:
                words.append(f" 👤x{payload['watchingCount']}")
            if 'likeCount' in payload:
                words.append(f" ❤x{payload['likeCount']}")
        elif signal_name == "CommonStateSignalTopUsers":
            tops = [user_info(u) for u in payload['user']]
            words.append(f"\r\n🥇{tops[0]}")
            words.append(f"\r\n🥈{tops[1]}")
            words.append(f"\r\n🥉{tops[2]}")
        elif signal_name == "CommonStateSignalRecentComment":
            words = list()
            for comment in payload['comment']:
                his_words = list()
                # 消息类型
                his_words.append(message_types.get(msg_type, "(????????)"))
                # 信号类型
                if signal_name:
                    his_words.append(signal_types.get(signal_name, "[????????]"))
                # 内容信息
                user = user_info(comment)
                content = comment['content']
                send_time = arrow.get(int(comment['sendTimeMs']), tzinfo="Asia/Shanghai").format("HH:mm:ss")
                his_words.append(f"{{{send_time}}}{user} {content}")
                full_comment = "".join(his_words) + "\r\n"
                words.append(full_comment)
        elif signal_name == "CommonNotifySignalKickedOut":
            words.append(f"{payload['reason']}")
        elif signal_name == "CommonNotifySignalViolationAlert":
            words.append(f"{payload['violationContent']}")
        elif signal_name == "CommonNotifySignalLiveManagerState":
            # MANAGER_STATE_UNKNOWN = 0
            # MANAGER_ADDED = 1
            # MANAGER_REMOVED = 2
            # IS_MANAGER = 3
            words.append(f"{payload['state']}")
        this_words = "".join(words)
        if this_words.endswith("\r\n"):
            this_words = this_words[:-2]
        messages.append(this_words)
    return messages


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
    ready = False

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
        self.ready = True


class AcWebSocket:
    ws_link = None
    config = None
    _main_thread = None
    tasks = dict()
    commands = dict()
    unread = []
    is_register_done = False
    live_room = None
    player_config = None
    _console = console.Console(width=100)
    live_room_msg_bans = []
    is_close = True

    def __init__(self, acer):
        self.acer = acer
        # websocket.enableTrace(True)
        self.ws_link = random.choice(websocket_links)
        self.config = AcWsConfig(self.acer)
        self.protos = AcProtos(self)
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
                ping_interval=10, ping_timeout=5,
                skip_utf8_validation=True,
                origin="live.acfun.cn",
            )
        self._main_thread = threading.Thread(target=_run)
        self._main_thread.start()
        self.is_close = False
        return self

    def wait4ready(self):
        while self.config.ready is False:
            print('wait...')
            time.sleep(1)
        return True

    def add_task(self, seqId: int, command, content):
        if self.is_close is True:
            return False
        if f"{seqId}" not in self.tasks:
            self.tasks[f"{seqId}"] = dict()
        self.tasks[f"{seqId}"]["send"] = {"command": command, "content": content, "time": time.time()}
        if command not in self.commands:
            self.commands[command] = []
        self.commands[command].append({"seqId": f"{seqId}", "way": "send", "time": time.time()})
        # print(f"send: [{seqId}] {command}")
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
            self.task(*self.protos.ClientConfigGet_Request())
            print(f"did       : {self.config.did}")
            print(f"userId    : {self.config.userId}")
            print(f"ssecurity : {self.config.ssecurity}")
            print(f"sessKey   : {self.config.sessKey.decode()}")
            self.is_register_done = True
            print(">>>>>>>> AcWebsocket Registed<<<<<<<<<")
        elif command == 'Basic.ClientConfigGet':
            self.task(*self.protos.KeepAlive_Request())
            self.protos.client_config = result
            print(">>>>>>>> AcWebsocket  Ready  <<<<<<<<<")
        elif command == 'LiveCmd.ZtLiveCsEnterRoomAck':
            self.live_room = self.protos.live_room
            self.task(*self.protos.ZtLiveCsHeartbeat_Request())
            self.task(*self.protos.ZtLiveInteractiveMessage_Request())
            print(">>>>>>>> AcWebsocket EnterRoom <<<<<<<<")
            live_data = json.loads(self.live_room.get('videoPlayRes', "")).get('liveAdaptiveManifest', [])[0]
            live_adapt = live_data.get('adaptationSet', {}).get('representation', {})
            if self.player_config is None:
                pyperclip.copy(live_adapt[2]['url'])
                print(f"未设置PotPlayer 已复制串流地址 请自行播放")
            else:
                create_time = self.live_room.get('liveStartTime', 0) // 1000
                start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(create_time))
                live_title = " ".join([self.live_room['caption'], f"🎬 {start_time}"])
                potplayer = self.player_config['player_path']
                print(f"[{potplayer}] 开始播放...... {live_title}")
                live_obs_stream = live_adapt[self.player_config['quality']]['url']
                subprocess.Popen([potplayer, live_obs_stream, "/title", f'"{live_title}"'], stdout=subprocess.PIPE)
        if command.startswith("LivePush.") and result:
            msg = ac_live_room_reader(result, self.live_room_msg_bans)
            for n in msg:
                self._console.print(n)

    def _register(self, ws):
        print(">>>>>>> AcWebsocket Connecting<<<<<<<<")
        self.task(*self.protos.BasicRegister_Request())

    def _message(self, ws, message):
        self.ans_task(*self.protos.decode(message))

    def _keep_alive_request(self, ws, message):
        self.add_task(*self.protos.BasicPing_Request())

    def _keep_alive_response(self, ws, message):
        if self.is_register_done:
            self.add_task(*self.protos.KeepAlive_Request())

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
        self.add_task(*self.protos.Unregister_Request())
        self.is_close = True
        self.ws.close()

    def restart(self):
        print(">>>>>>>> AcWebsocket  RESTART <<<<<<<<<")
        self.close()
        self.run()

    def im_get_sessions(self):
        message = self.protos.MessageSession_Request()
        return self.task(*message)

    def im_session_start(self, uid: int):
        message = self.protos.SessionCreate_Request(uid)
        return self.task(*message)

    def im_session_close(self, uid: int):
        message = self.protos.SessionRemove_Request(uid)
        return self.task(*message)

    def im_pull_message(self, uid: int, minSeq: int, maxSeq: int, count: int = 10):
        message = self.protos.MessagePullOld_Request(uid, minSeq, maxSeq, count)
        return self.task(*message)

    def im_send(self, uid: int, content: str):
        message = self.protos.MessageContent_Request(uid, content)
        return self.task(*message)

    def im_send_image(self, uid: int, image_data: bytes):
        message = self.protos.MessageImage_Request(uid, image_data)
        return self.task(*message)

    def live_enter_room(self, uid: int, room_bans: [list, None] = None,
                        potplayer: [str, None] = None, quality: int = 1):
        if isinstance(potplayer, str) and os.path.isfile(potplayer):
            self.player_config = {"player_path": potplayer, "quality": quality}
        self.live_room_msg_bans = [] if room_bans is None else room_bans
        cmd = self.protos.ZtLiveCsEnterRoom_Request(uid)
        return self.task(*cmd)

