# coding=utf-8
from acfunsdk import Acer

# 实例化一个Acer
acer = Acer(debug=True)

# 通过链接直接获取内容对象
demo_bangumi = acer.get("https://www.acfun.cn/bangumi/aa6003696")
print(demo_bangumi)

# 剧季数据
seasons = demo_bangumi.season_data()
print("seasons:", seasons)

# 剧集数据
episodes = demo_bangumi.episode_data()
print("episodes", episodes)


# 对某集进行操作
def episode_action(n: int = 1):
    # 调整集数
    demo_bangumi.set_video(n)
    # 弹幕对象
    danmaku = demo_bangumi.danmaku()
    # 弹幕列表: 列表中是单条弹幕对象，可以点赞/屏蔽/举报
    danmaku.list()
    # 发送弹幕: 在1s位置发送666
    danmaku.add('666', 1000)
    # 评论对象
    comment = demo_bangumi.comment()
    # 获取所有评论
    comment.get_all_comment()
    # 所有单条评论对象，可以点赞/删除
    comment.list()
    # 提交评论
    comment.add('comment from acfunSDK')

    # 点赞/取消
    demo_bangumi.like()
    # demo_bangumi.like_cancel()
    # 收藏/取消
    demo_bangumi.favorite_add()
    # demo_bangumi.favorite_cancel()
    # 投蕉
    demo_bangumi.banana()


if __name__ == '__main__':
    episode_action()
    pass
