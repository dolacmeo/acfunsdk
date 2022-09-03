# coding=utf-8
from acfun import Acer

# 实例化一个Acer
acer = Acer(debug=True)


# 通过链接直接获取内容对象
demo_live = acer.get("https://live.acfun.cn/live/378269")
print(demo_live)

# 直播信息
infos = demo_live.infos()
print(infos)

# 直播UP主
up = demo_live.AcUp()
print(up)

# UP主投稿
for video in demo_live.contents():
    print(video)

# 发送弹幕
demo_live.push_danmaku("666")

# 循环点赞: 点10次，需要10s
demo_live.like(10)

# 当前礼物列表
gifts = demo_live.gift_list()
print(gifts)

# 查看余额
balance = demo_live.my_balance()
print(balance)

# 送出礼物: 投5蕉 2次
demo_live.send_gift(1, 5, 2)

# 播放直播: 需要定义本地potplayer路径
player = [r"C:\Program Files\PotPlayer64\PotPlayerMini64.exe", 2]
demo_live.playing(*player)

# 观看弹幕: 可同时调起直播，方法同上
bans = [
    # "ZtLiveScActionSignal",  # 互动消息
    "ZtLiveScStateSignal",  # 状态消息
    "ZtLiveScNotifySignal",  # 房管消息
]
demo_live.watching_danmaku(bans, *player)

