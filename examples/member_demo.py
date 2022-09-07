# coding=utf-8
from acfunsdk import Acer

# 实例化一个Acer
acer = Acer(debug=True)

# 通过链接直接获取内容对象
demo_up = acer.get("https://www.acfun.cn/u/39088")
print(demo_up)

# 读取页面信息
demo_up.loading()

# 直播对象
demo_up.AcLive()

# 关注/特别/取消
demo_up.follow_add()
# demo_up.follow_add(True)
# demo_up.follow_add(False)
# demo_up.follow_remove()

# 发布的视频
for video in demo_up.video():
    print(video)

# 发布的文章
for article in demo_up.article():
    print(article)

# 他的合集
for album in demo_up.album():
    print(album)

# 他的关注
for member in demo_up.following():
    print(member)

# 他的粉丝
for member in demo_up.followed():
    print(member)

