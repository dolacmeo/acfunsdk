# coding=utf-8
from acfunsdk import Acer

# 实例化一个Acer
acer = Acer(debug=True)


def acfun_search(keyword: str, s_type: [str, None] = None, page: int = 1):
    print("search:", keyword)
    obj = acer.AcSearch(keyword, s_type)
    first_page = obj.page(page)
    for i, item in enumerate(first_page):
        print(f"{(i+1):0>2}", item)


if __name__ == '__main__':
    acfun_search("爆蕉一夏")
    pass
