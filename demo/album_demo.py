# coding=utf-8
from acfun import Acer

# 实例化一个Acer
acer = Acer(debug=True)

# 通过链接直接获取内容对象
demo_album = acer.get("https://www.acfun.cn/a/aa6001205")
print(demo_album)

# 简介信息
print(demo_album.info)

# 合集内容
for item in demo_album.list():
    print(item)

# 收藏/取消
demo_album.favorite_add()
# demo_album.favorite_cancel()
