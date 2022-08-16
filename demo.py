# coding=utf-8
from acfun import Acer

__author__ = 'dolacmeo'

# todo 保存弹幕ass
# todo 保存文章
# todo cil

# todo 实用功能
#   发稿件
#   传视频
#   支持ws：IM，直播互动
#   离线查看保存资源

# 实例化一个Acer
acer = Acer(debug=True)


def acfun_index():
    # a站首页解析展示
    index_obj = acer.AcIndex()
    # 首页所有页面区块
    print(index_obj.index_pagelets)
    # banner
    print(index_obj.get('banner', True))
    # 轮播+顶栏
    print(index_obj.get('pagelet_top_area', True))
    # 猴子推荐
    print(index_obj.get('pagelet_monkey_recommend', True))
    # 动画
    print(index_obj.get('pagelet_douga', True))
    # 舞蹈
    print(index_obj.get('pagelet_dance', True))


def acfun_channel():
    # 通过地址快捷 实例化
    donga = acer.get('https://www.acfun.cn/v/list1/index.htm')
    print(donga)
    # 主频道热词
    print(donga.hot_words())
    # 主频道区块
    print(donga.blocks())
    # 通过id 实例化
    zhaiwu = acer.AcChannel(134)
    print(zhaiwu)
    # 栏目视频列表
    vs = zhaiwu.videos(1, 'rankScore', 'all', 'default')
    for wu in vs:
        print(wu)


def acfun_wenzhang():
    # 文章区
    wz = acer.AcWen()
    # 获取
    print(wz.feed(True))
    print(wz.feed(True))
    print(wz.feed(True))
    # 从缓存实例化文章对象
    data = wz.article_data[3]
    acer.AcArticle(data['articleId'], data)
    # 清除缓存
    wz.clean_cache()


def acfun_live():
    live_index = acer.AcLive()
    # 所有当前直播房间
    all_room = live_index.list()
    for room in all_room[:10]:
        print(room)
    # 综合排名第三
    room3 = all_room[2]
    print(room3)
    # 主播投稿视频
    print(room3.contents())
    # 获取串流地址，可直接调起potplayer播放
    player = r"C:\Program Files\PotPlayer64\PotPlayerMini64.exe"
    # 0[480p], 1[720p], 2[1080p], 3[4k]
    room3.playing(2, player)


def acfun_content():
    # 快捷获取
    demo_video = acer.get('https://www.acfun.cn/v/ac4741185')
    demo_article = acer.get('https://www.acfun.cn/a/ac2292652')
    demo_bangumi = acer.get('https://www.acfun.cn/bangumi/aa5023295')
    demo_live = acer.get('https://live.acfun.cn/live/32899113')
    demo_up = acer.get('https://www.acfun.cn/u/11524392')
    # 动态 暂时有问题，目前只能从列表获取
    # demo_moment = acer.get('https://www.acfun.cn/moment/am2752247')
    for x in [demo_video, demo_article, demo_bangumi, demo_live, demo_up]:
        print(x)


def acfun_video():
    # 互动功能需要用户登录
    demo_video = acer.get('https://www.acfun.cn/v/ac4741185')
    print(demo_video)
    # UP主
    print(demo_video.up())
    # 弹幕
    demo_danmaku = demo_video.danmaku()
    print(demo_danmaku)
    # 弹幕列表
    # demo_danmaku.list()
    # 弹幕数据，可保存
    # demo_danmaku.to_json()
    # demo_danmaku.add('在1秒处发弹幕', 1000)
    # 评论
    demo_comment = demo_video.comment()
    print(demo_comment)
    # 获取所有评论
    # demo_comment.get_all_comment()
    # 热评
    # demo_comment.hot()
    # 评论列表
    # demo_comment.list()
    # 添加评论
    # demo_comment.add('噫~~~')
    # 获取评论楼层
    # demo_comment.get(1)
    # 通过id获取评论
    # demo_comment.find(66945938)
    # 点赞
    # demo_video.like()
    # demo_video.like_cancel()
    # 收藏
    # demo_video.favorite_add()
    # demo_video.favorite_cancel()
    # 投蕉
    # demo_video.banana(5)
    # 奥里给！(赞 藏 蕉 弹 评)
    # demo_video.aoligei(danmu=True, comment=True)
    # 下载视频 保存至 "\download\video\ac....mp4"
    # demo_video.download()


def acfun_article():
    demo_article = acer.get('https://www.acfun.cn/a/ac2292652')
    print(demo_article)
    # 文章功能大多与视频重叠
    # 输出纯文字版
    print(demo_article.contents())


def print_histories():
    # 在调试模式下输出所有网络请求记录
    if acer.debug is True:
        for x in acer.client.history:
            print(x)


if __name__ == '__main__':
    # 以下仅部分功能展示
    # 登录用户(成功登录后会自动保存 '<用户名>.json')
    # acer.login('dolacmeo@qq.com', 'balalabalala')
    # 读取用户(读取成功登录后保存的 '<用户名>.json')
    # acer.loading('dolacmeo@qq.com')
    # 首页
    # acfun_index()
    # 频道
    # acfun_channel()
    # 文章区
    # acfun_wenzhang()
    # 直播
    # acfun_live()
    # 各种类型对象
    # acfun_content()
    # 视频对象
    # acfun_video()
    # 文章对象
    # acfun_article()
    # 调试模式下调取访问历史
    # print_histories()
    pass
