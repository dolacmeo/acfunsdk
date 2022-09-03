# coding=utf-8
from acfun import Acer

# 实例化一个Acer
acer = Acer(debug=True)

# 实例化首页
acfun_index = acer.AcIndex()
# 页面分区列表
# 分区命名均以 pagelet_ 开头
# 使用get函数时 pagelet_ 开头可省略
print("pagelets:", acfun_index.index_pagelets)


# 导航
def show_nav():
    navs = acfun_index.nav_list()
    print('navs:')
    for nav in navs:
        print(nav)


# Banner
def show_banner(obj: bool = True):
    banner = acfun_index.get('banner', obj)
    if obj is False:
        return banner
    print(banner)


# 轮播+顶栏
def show_top_area(obj: bool = True):
    top_area = acfun_index.get('pagelet_top_area', obj)
    if obj is False:
        return top_area
    print("slider:")
    for image in top_area['slider']:
        print(image)
    print("items:")
    for item in top_area['items']:
        print(item)


# 猴子推荐
def show_monkey_recommend(obj: bool = True):
    monkey_recommend = acfun_index.get('pagelet_monkey_recommend', obj)
    if obj is False:
        return monkey_recommend
    print("items:")
    for item in monkey_recommend['items']:
        print(item)
    print("right AD:")
    print(monkey_recommend['ad'])


# 正在直播
def show_live(obj: bool = True):
    on_live = acfun_index.get('pagelet_live', obj)
    if obj is False:
        return on_live
    print("items:")
    for item in on_live['items']:
        print(item)
    print("right AD:")
    print(on_live['ad'])


# 香蕉榜 + 文章
def show_list_banana(obj: bool = True):
    list_banana = acfun_index.get('pagelet_list_banana', obj)
    if obj is False:
        return list_banana
    for day in ['d1', 'd3', 'd7']:
        print(f"香蕉榜 {day}:")
        for index, item in enumerate(list_banana[day]):
            print(f"{(index+1):0>2}", item)
    print("文章:")
    for tag in list_banana['article'].keys():
        print(f"文章-{tag}:")
        for index, item in enumerate(list_banana['article'][tag]):
            print(f"{(index+1):0>2}", item)


# 动画(带大图推荐的栏目)
def show_douga(obj: bool = True):
    douga = acfun_index.get('pagelet_douga', obj)
    if obj is False:
        return douga
    print("channel:", douga['channel'])
    print("icon:", douga['icon'])
    print('links:')
    for link in douga['links']:
        print(link)
    print("items:")
    for item in douga['items']:
        print(item)
    for day in ['d1', 'd3', 'd7']:
        print(f"排行榜 {day}:")
        for index, item in enumerate(douga['rank'][day]):
            print(f"{(index+1):0>2}", item)


# 番剧
def show_bangumi_list(obj: bool = True):
    bangumi_list = acfun_index.get('pagelet_bangumi_list', obj)
    if obj is False:
        return bangumi_list
    print("channel:", bangumi_list['channel'])
    print("icon:", bangumi_list['icon'])
    print("schedule:")
    for weekday, dayshow in enumerate(bangumi_list['schedule']):
        weekday += 1
        print(f"day-{weekday}:")
        for i, show in enumerate(dayshow):
            print(f"{(i+1):0>2}", show)
    print("recommend:")
    for show in bangumi_list['recommend']:
        print(show)
    print("anli:")
    for show in bangumi_list['anli']:
        print(show)


# 舞蹈(一般栏目，无大图推荐)
def show_dance(obj: bool = True):
    dance = acfun_index.get('pagelet_dance', obj)
    if obj is False:
        return dance
    print("channel:", dance['channel'])
    print("icon:", dance['icon'])
    print('links:')
    for link in dance['links']:
        print(link)
    print("items:")
    for item in dance['items']:
        print(item)
    for day in ['d1', 'd3', 'd7']:
        print(f"排行榜 {day}:")
        for index, item in enumerate(dance['rank'][day]):
            print(f"{(index+1):0>2}", item)


# 底部信息栏
def show_footer(obj: bool = True):
    footer = acfun_index.get('footer', obj)
    if obj is False:
        return footer
    print('links:')
    for tag in footer['links']:
        print(f"links-{tag}:")
        for link in footer['links'][tag]:
            print(link)
    print('infos:')
    for info in footer['infos']:
        print(info)
    print('copyright')
    for k, v in footer['copyright'].items():
        print(f"{k}: {v}")


if __name__ == '__main__':
    # 通过调整传参 obj
    # 可选返回实例化对象 或直接返回数据
    # show_nav()
    show_banner()
    show_top_area()
    # show_monkey_recommend()
    # show_live()
    # show_list_banana()
    # show_douga()
    # show_bangumi_list()
    # show_dance()
    footer = show_footer(False)
    print(footer)
    pass
