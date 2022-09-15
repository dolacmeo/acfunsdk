# coding=utf-8
from acfunsdk import Acer

# 实例化一个Acer
acer = Acer(debug=True)


# 通过链接直接获取内容对象
# 目前支持 9种类型：
def acer_get():
    # 视  频: https://www.acfun.cn/v/ac4741185
    demo_video = acer.get("https://www.acfun.cn/v/ac4741185")
    print(demo_video)
    # 文  章: https://www.acfun.cn/a/ac16695813
    demo_article = acer.get("https://www.acfun.cn/a/ac16695813")
    print(demo_article)
    # 合  集: https://www.acfun.cn/a/aa6001205
    demo_album = acer.get("https://www.acfun.cn/a/aa6001205")
    print(demo_album)
    # 番  剧: https://www.acfun.cn/bangumi/aa5023295
    demo_bangumi = acer.get("https://www.acfun.cn/bangumi/aa5023295")
    print(demo_bangumi)
    # 个人页: https://www.acfun.cn/u/39088
    demo_up = acer.get("https://www.acfun.cn/u/39088")
    print(demo_up)
    # 动  态: https://www.acfun.cn/moment/am2797962
    demo_moment = acer.get("https://www.acfun.cn/moment/am2797962")
    print(demo_moment)
    # 直  播: https://live.acfun.cn/live/378269
    demo_live = acer.get("https://live.acfun.cn/live/378269")
    print(demo_live)
    # 分  享: https://m.acfun.cn/v/?ac=37086357
    demo_share = acer.get("https://m.acfun.cn/v/?ac=37086357")
    print(demo_share)
    # 涂鸦(单页): https://hd.acfun.cn/doodle/knNWmnco.html
    demo_doodle = acer.get("https://hd.acfun.cn/doodle/knNWmnco.html")
    print(demo_doodle)


# 通过ID直接获取内容对象
# 目前支持 8种类型：
def acer_get_byid():
    # 视  频: https://www.acfun.cn/v/ac4741185
    demo_video = acer.AcVideo(4741185)
    print(demo_video)
    # 文  章: https://www.acfun.cn/a/ac16695813
    demo_article = acer.AcArticle(16695813)
    print(demo_article)
    # 合  集: https://www.acfun.cn/a/aa6001205
    demo_album = acer.AcAlbum(6001205)
    print(demo_album)
    # 番  剧: https://www.acfun.cn/bangumi/aa5023295
    demo_bangumi = acer.AcBangumi(5023295)
    print(demo_bangumi)
    # 个人页: https://www.acfun.cn/u/39088
    demo_up = acer.AcUp(dict(userId=39088))
    print(demo_up)
    # 动  态: https://www.acfun.cn/moment/am2797962
    demo_moment = acer.moment.get(2797962)
    print(demo_moment)
    # 直  播: https://live.acfun.cn/live/378269
    demo_live = acer.AcLiveUp(378269)
    print(demo_live)
    # 涂鸦(单页): https://hd.acfun.cn/doodle/knNWmnco.html
    demo_doodle = acer.AcDoodle("knNWmnco")
    print(demo_doodle)


# 调取内容对象
def acer_objs():
    # 首页
    acfun_index = acer.AcIndex()
    # 频道
    acfun_channel = acer.AcChannel(1)
    # 文章区
    acfun_wen = acer.AcWen()
    # 榜单
    acfun_rank = acer.AcRank()
    # 搜索
    acfun_search = acer.AcSearch()
    # 保存工具
    acsaver = acer.AcSaver()


# 登陆后可用(功能太多，以下仅简略列出)
def acer_logined():
    # 登录方式二选一
    # 登录用户(成功登录后会自动保存 '<用户名>.cookies')
    # 请注意保存，防止被盗
    # acer.login(username='you@email.com', password='balalabalala')
    # 读取用户(读取成功登录后保存的 '<用户名>.cookies')
    # acer.loading(username='13800138000')
    # 每日签到，领香蕉🍌
    # acer.signin()
    # 查询我的余额
    # acer.acoin()
    # 设置签名
    # acer.update_signature("My signature setup from acfunSDK.")
    # 我的消息
    print(acer.message.unread)
    print(acer.message.reply())
    print(acer.message.like())
    print(acer.message.at())
    print(acer.message.gift())
    print(acer.message.notice())
    print(acer.message.system())
    # 我的收藏
    # acer.favourite.video_list()
    # acer.favourite.article_list()
    # acer.favourite.bangumi_list()
    # acer.favourite.album_list()
    # 我的关注分组
    f_groups = acer.follow_groups()
    print(f_groups)
    # 分组增删改
    # acer.follow_group_add("acfunSDK")
    # acer.follow_group_remove(1)
    # acer.follow_group_rename(1, "acfunSDK")
    # 观看历史
    # acer.history()
    # 我的粉丝
    # acer.my_fans()
    # 我发布的文章
    # acer.my_articles()
    # 我发布的视频
    # acer.my_videos()
    # 数据中心
    # acer.data_center()
    # acer.data_center_detail()
    # 我的直播设置
    # acer.get_live_config()
    # 发文章视频
    # 暂不支持，防止滥用
    pass


if __name__ == '__main__':
    acer_get()
    # acer_get_byid()
    # acer_objs()
    # acer_logined()
    pass
