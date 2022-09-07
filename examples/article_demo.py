# coding=utf-8
from acfunsdk import Acer

# 实例化一个Acer
acer = Acer(debug=True)

# 通过链接直接获取内容对象
demo_article = acer.get("https://www.acfun.cn/a/ac32633020")
print(demo_article)

# 文章UP主
up = demo_article.up()
print(up)

# 文章推荐
recommends = demo_article.recommends()

# AcSaver
saver = demo_article.saver()


# 对某P进行操作
def action():
    # 评论对象
    comment = demo_article.comment()
    # 获取所有评论
    comment.get_all_comment()
    # 所有单条评论对象，可以点赞/删除
    comment.list()
    # 提交评论
    comment.add('comment from acfunSDK')

    # 点赞/取消
    demo_article.like()
    # demo_article.like_cancel()
    # 收藏/取消
    demo_article.favorite_add()
    # demo_article.favorite_cancel()
    # 投蕉
    demo_article.banana()


if __name__ == '__main__':
    action()
    pass
