# coding=utf-8
from acfun import Acer

# 实例化一个Acer
acer = Acer(debug=True)


# 从首页获取频道对象
def get_channel_from_index(index):
    acfun_index = acer.AcIndex()
    nav_list = acfun_index.nav_list()
    return nav_list[index]


# 从链接获取频道对象
def get_channel_from_link(link):
    return acer.get(link)


# 通过id 实例化
def get_channel_from_id(cid: int):
    return acer.AcChannel(cid)


# 主栏目可用
def show_channel_main(channel_obj):
    # 初始化
    channel_obj.loading()
    print(channel_obj)
    # 主频道热词
    print(channel_obj.hot_words())
    # 主频道排行 默认日榜
    acrank = channel_obj.ranks(limit=10)
    print('ranks:')
    for i, item in enumerate(acrank.contents()):
        print(f"{(i+1):0>2}", item)
    # 主频道区块
    blocks = channel_obj.blocks()
    print("blocks:")
    for i, block in enumerate(blocks):
        print(block)
        if i == 0:  # 内容太多了，这里只展示首个区块
            for content in block.contents():
                print("     ", content)
                for item in content.list():
                    print("         ", item)


# 子栏目可用
def show_channel_sub(channel_obj):
    print(channel_obj)
    # 频道排行 默认日榜
    acrank = channel_obj.ranks(limit=10)
    print('ranks:')
    for i, item in enumerate(acrank.contents()):
        print(f"{(i+1):0>2}", item)
    print("videos:")
    for index, video in enumerate(channel_obj.videos()):
        print(f"{(index+1):0>2}", video)


# 文章区主频道
def show_article_channel():
    article = get_channel_from_link("https://www.acfun.cn/v/list63/index.htm")
    # 初始化
    article.loading()
    print(article)
    # 频道排行 默认日榜
    acrank = article.ranks(limit=10)
    print('ranks:')
    for i, item in enumerate(acrank.contents()):
        print(f"{(i+1):0>2}", item)
    # 主频道区块
    blocks = article.blocks()
    print("blocks:")
    for i, block in enumerate(blocks):
        print(block)
        if 0 < i < 2 or i > 8:  # 内容太多了，这里只展示部分区块
            for content in block.contents():
                print("     ", content)
                for item in content.list():
                    print("         ", item)


# 文章区动态更新，无限下拉
def show_article_feed(times: int = 2):
    acwen = acer.AcWen()
    count = 0
    while times > 0:
        result = acwen.feed()
        times -= 1
        if result is None:
            break
        for item in result:
            count += 1
            print(f"{count:0>3}", item)


if __name__ == '__main__':
    # 可选返回实例化对象 或直接返回数据
    # demo仅展示对象
    from_index = get_channel_from_index(5)
    show_channel_main(from_index)
    from_cid = get_channel_from_id(134)
    show_channel_sub(from_cid)
    # show_article_channel()
    # show_article_feed()

