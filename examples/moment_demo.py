# coding=utf-8
from acfun import Acer

# 实例化一个Acer
acer = Acer(debug=True)

# 通过Feed获取动态列表
# feeds = acer.moment.feed()
# demo_moment = feeds[0]

# 通过链接直接获取内容对象
demo_moment = acer.get("https://www.acfun.cn/moment/am2811516")
print(demo_moment)

# 动态UP
acup = demo_moment.up()
print(acup)

# 评论对象
comment = demo_moment.comment()
# 获取所有评论
comment.get_all_comment()
# 所有单条评论对象，可以点赞/删除
comment.list()
# 提交评论
comment.add('comment from acfunSDK')

# 投蕉
demo_moment.banana()

