# coding=utf-8
from acfun import Acer

# 实例化一个Acer
acer = Acer(debug=True)

# 通过链接直接获取内容对象
demo_video = acer.get("https://www.acfun.cn/v/ac33819914")
print(demo_video)

# 视频UP主
up = demo_video.up()
print(up)

# 联合稿件合作数据
staff = demo_video.staff()
print(staff)

# AcSaver
saver = demo_video.saver()


# 对某P进行操作
def part_action(n: int = 1):
    # 调整当前Part
    demo_video.set_video(n)
    # 弹幕对象
    danmaku = demo_video.danmaku()
    # 弹幕列表: 列表中是单条弹幕对象，可以点赞/屏蔽/举报
    danmaku.list()
    # 发送弹幕: 在1s位置发送666
    danmaku.add('666', 1000)
    # 评论对象
    comment = demo_video.comment()
    # 获取所有评论
    comment.get_all_comment()
    # 所有单条评论对象，可以点赞/删除
    comment.list()
    # 提交评论
    comment.add('comment from acfunSDK')

    # 点赞/取消
    demo_video.like()
    # demo_video.like_cancel()
    # 收藏/取消
    demo_video.favorite_add()
    # demo_video.favorite_cancel()
    # 投蕉
    demo_video.banana()
    # 一键奥里给！(赞 藏 蕉 弹 评)
    demo_video.aoligei(True, True)


if __name__ == '__main__':
    part_action()
    pass
