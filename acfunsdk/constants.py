# coding=utf-8
# Constants for acfunsdk

resource_type_map = {
    "1": "AcBangumi",  # 番剧
    "2": "AcVideo",  # 视频稿件
    "3": "AcArticle",  # 文章稿件
    "4": "AcAlbum",  # 合辑
    "5": "AcUp",  # 用户
    "6": "AcComment",  # 评论
    # "8": "私信",
    "10": "AcMoment",  # 动态
}

routes_type_map = {
    "bangumi": "AcBangumi",  # 番剧
    "video": "AcVideo",  # 视频稿件
    "article": "AcArticle",  # 文章稿件
    "album": "AcAlbum",  # 合辑
    "up": "AcUp",  # 用户
    "live": "AcLiveUp",  # 用户直播
    "moment": "AcMoment",  # 用户动态
    "doodle": "AcDoodle",  # 涂鸦页面
}

type_routes_map = {v: k for k, v in routes_type_map.items()}

resource_type_str_map = {
    "1": "番剧",  # AcBangumi
    "2": "视频",  # AcVideo
    "3": "文章",  # AcArticle
    "4": "合辑",  # AcAlbum
    "5": "用户",  # AcUp
    "6": "评论",  # AcComment
    "10": "动态",  # AcMoment
}