# coding=utf-8
# LastCheck: 2022/08/16

__author__ = 'dolacmeo'

header = {
    "Referer": "https://www.acfun.cn/",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/104.0.5112.102 Safari/537.36'
}

scheme = "https"

domains = {
    "main": "www.acfun.cn",
    "msg": "message.acfun.cn",
    "user": "member.acfun.cn",
    "live": "live.acfun.cn",
    "mobile": "m.acfun.cn",
    "id_api": "id.app.acfun.cn"
}

routes = {
    "index": f"{scheme}://{domains['main']}",
    "ico": f"{scheme}://{domains['main']}/favicon.ico",
    "video": f"{scheme}://{domains['main']}/v/ac",
    "article": f"{scheme}://{domains['main']}/a/ac",
    "album": f"{scheme}://{domains['main']}/a/aa",
    "bangumi": f"{scheme}://{domains['main']}/bangumi/aa",
    "up": f"{scheme}://{domains['main']}/u/",
    'moment': f"{scheme}://{domains['main']}/moment/am",
    "live": f"{scheme}://{domains['live']}/live/",
    "share": f"{scheme}://{domains['mobile']}/v/?ac=",
    'feeds': f"{scheme}://{domains['main']}/member/feeds",
    'im': f"{scheme}://{domains['msg']}/im",
    "emot": f"{scheme}://{domains['main']}/emot/",
    "app": f"{scheme}://{domains['main']}/app/",
}

apis = {
    'cdn_domain': f"{scheme}://{domains['main']}/rest/pc-direct/image/cdnDomain",
    'message': f"{scheme}://{domains['msg']}/",
    'token': f"{scheme}://{domains['id_api']}/rest/web/token/get",
    'nav': f"{scheme}://{domains['main']}/rest/pc-direct/page/queryNavigators",
    'emot': f"{scheme}://{domains['main']}/rest/pc-direct/emotion/getUserEmotion",
    'login': f"{scheme}://{domains['id_api']}/rest/web/login/signin",
    'logout': f"{scheme}://{domains['id_api']}/rest/web/logout",
    'signIn': f"{scheme}://{domains['main']}/rest/pc-direct/user/signIn",
    'personalInfo': f"{scheme}://{domains['main']}/rest/pc-direct/user/personalInfo",
    'personalBasicInfo': f"{scheme}://{domains['main']}/rest/pc-direct/user/personalBasicInfo",
    'acoinBalance': f"{scheme}://{domains['main']}/rest/pc-direct/pay/wallet/acoinBalance",
    'userInfo': f"{scheme}://{domains['main']}/rest/pc-direct/user/userInfo",
    'getStaff': f"{scheme}://{domains['main']}//rest/pc-direct/staff/getStaff",
    'updateSignature': f"{scheme}://{domains['main']}/rest/pc-direct/user/updateSignature",
    'channel_list': f"{scheme}://{domains['user']}/common/api/getChannelList",
    'rank_list': f"{scheme}://{domains['main']}/rest/pc-direct/rank/channel",
    'album_list': f"{scheme}://{domains['main']}/rest/pc-direct/arubamu/content/list",
    'search': f"{scheme}://{domains['main']}/search",
    'search_keywords': f"{scheme}://{domains['main']}/rest/pc-direct/homePage/searchDefault",
    'history': f"{scheme}://{domains['main']}/rest/pc-direct/browse/history/list",

    'get_users': f"{scheme}://{domains['main']}/rest/pc-direct/user/getUserCardList",  # POST form:ids
    'follow': f"{scheme}://{domains['main']}/rest/pc-direct/relation/follow",
    'follow_fans': f"{scheme}://{domains['main']}/rest/pc-direct/relation/getFollows",
    'follow_groups': f"{scheme}://{domains['main']}/rest/pc-direct/relation/getGroups",
    'follow_group': f"{scheme}://{domains['main']}/rest/pc-direct/relation/group",
    'favorite_add': f"{scheme}://{domains['main']}/rest/pc-direct/favorite",
    'favorite_remove': f"{scheme}://{domains['main']}/rest/pc-direct/unFavorite",
    'favorite_video': f"{scheme}://{domains['main']}/rest/pc-direct/favorite/resource/dougaList",
    'favorite_article': f"{scheme}://{domains['main']}/rest/pc-direct/favorite/resource/articleList",
    'favorite_bangumi': f"{scheme}://{domains['main']}/rest/pc-direct/favorite/resource/bangumiList",
    'favorite_album': f"{scheme}://{domains['main']}/rest/pc-direct/favorite/resource/albumList",

    'like_add': f"{scheme}://kuaishouzt.com/rest/zt/interact/add",
    'like_delete': f"{scheme}://kuaishouzt.com/rest/zt/interact/delete",

    'video_favorite_list': f"{scheme}://{domains['main']}/rest/pc-direct/favorite/folder/list",
    'video_favorite_group_add': f"{scheme}://{domains['main']}/rest/pc-direct/favorite/folder/add",
    'video_favorite_group_update': f"{scheme}://{domains['main']}/rest/pc-direct/favorite/folder/update",
    'video_favorite_group_delete': f"{scheme}://{domains['main']}/rest/pc-direct/favorite/folder/delete",
    'throw_banana': f"{scheme}://{domains['main']}/rest/pc-direct/banana/throwBanana",

    'follow_feed': f"{scheme}://{domains['main']}/rest/pc-direct/feed/followFeedV2",
    'article_feed': f"{scheme}://{domains['main']}/rest/pc-direct/article/feed",

    'comment': f"{scheme}://{domains['main']}/rest/pc-direct/comment/list",
    'comment_floor': f"{scheme}://{domains['main']}/rest/pc-direct/comment/listByFloor",
    'comment_subs': f"{scheme}://{domains['main']}/rest/pc-direct/comment/sublist",
    'comment_add': f"{scheme}://{domains['main']}/rest/pc-direct/comment/add",
    'comment_delete': f"{scheme}://{domains['main']}/rest/pc-direct/comment/delete",
    'comment_like': f"{scheme}://{domains['main']}/rest/pc-direct/comment/like",
    'comment_unlike': f"{scheme}://{domains['main']}/rest/pc-direct/comment/unlike",
    'danmaku': f"{scheme}://{domains['main']}/rest/pc-direct/new-danmaku/list",
    'danmaku_add': f"{scheme}://{domains['main']}/rest/pc-direct/new-danmaku/add",
    'danmaku_get': f"{scheme}://{domains['main']}/rest/pc-direct/new-danmaku/pollByPosition",
    'danmaku_like': f"{scheme}://{domains['main']}/rest/pc-direct/new-danmaku/like",
    'danmaku_like_cancel': f"{scheme}://{domains['main']}/rest/pc-direct/new-danmaku/like/cancel",
    'danmaku_block_add': f"{scheme}://{domains['main']}/rest/pc-direct/new-danmaku/blockWords/add",
    'danmaku_block_delete': f"{scheme}://{domains['main']}/rest/pc-direct/new-danmaku/blockWords/delete",
    'danmaku_report': f"{scheme}://{domains['main']}/rest/pc-direct/new-danmaku/report",

    'member_posted': f"{scheme}://{domains['user']}/list/api/queryContributeList",
    'checkUserPermission': f"{scheme}://{domains['user']}/common/api/checkUserPermission",
    'dataCenter_overview': f"{scheme}://{domains['user']}/dataCenter/api/overview",
    'dataCenter_content': f"{scheme}://{domains['user']}/dataCenter/api/contentData",
    'dataCenter_live': f"{scheme}://{domains['user']}/dataCenter/api/liveData",

    'checkLiveAuth': f"{scheme}://{domains['user']}/common/api/checkLiveAuth",
    'getLiveTypeList': f"{scheme}://{domains['user']}/common/api/getLiveTypeList",
    'getUserLiveCut': f"{scheme}://{domains['user']}/liveToll/api/getUserLiveCut",
    'showFansClubApplyEntrance': f"{scheme}://{domains['user']}/common/api/showFansClubApplyEntrance",
    'checkFansClubAuth': f"{scheme}://{domains['user']}/interActive/api/checkFansClubAuth",
    'bind_ksaccount': f"{scheme}://{domains['id_api']}/rest/web/central/ksaccount/status",
    'live_obs_status': "https://api.kuaishouzt.com/rest/zt/live/web/obs/status",
    'live_obs_config': "https://api.kuaishouzt.com/rest/zt/live/web/obs/config",
    'live_play': "https://api.kuaishouzt.com/rest/zt/live/web/startPlay",
    'live_watching': "https://api.kuaishouzt.com/rest/zt/live/web/watchingList",
    'live_list': f"{scheme}://{domains['live']}/api/channel/list",
    'live_info': f"{scheme}://{domains['live']}/api/live/info",
    'live_up_contents': f"{scheme}://{domains['live']}/api/liveExtra/info",

    'app_download': f"{scheme}://{domains['main']}/rest/pc-direct/download/channel/packageUrl?channel=default",
    'face_catcher': f"{scheme}://{domains['main']}/face/api/getKconf",

    'image_upload_gettoken': f"{scheme}://{domains['main']}/rest/pc-direct/image/upload/getToken",
    'image_upload_resume': "https://upload.kuaishouzt.com/api/upload/resume",
    'image_upload_fragment': "https://upload.kuaishouzt.com/api/upload/fragment",
    'image_upload_complete': "https://upload.kuaishouzt.com/api/upload/complete",
    'image_upload_geturl': f"{scheme}://{domains['main']}/rest/pc-direct/image/upload/getUrlAfterUpload",

    'qrcode': "https://ksurl.cn/createqrcode",
}

pagelets_from_page = [
    "pagelet_banner",  # banner
    "pagelet_navigation",  # 导航栏
    'pagelet_top_area',  # 置顶
    'pagelet_monkey_recommend',  # 猴子推荐
    'pagelet_live',  # 直播
    'pagelet_spring_festival',  # 春季节日活动
    'pagelet_list_banana',  # 香蕉榜
    'footer',  # 页脚
]

pagelets_from_api = [
    "pagelet_header",  # 顶栏
    "pagelet_douga",  # 动画
    "pagelet_game",  # 游戏
    "pagelet_amusement",  # 娱乐
    "pagelet_bangumi_list",  # 番剧
    "pagelet_life",  # 生活
    "pagelet_tech",  # 科技
    "pagelet_dance",  # 舞蹈·偶像
    "pagelet_music",  # 音乐
    "pagelet_film",  # 影视
    "pagelet_fishpond",  # 鱼塘
    "pagelet_sport",  # 体育
]

pagelets_big = [
    "pagelet_douga",  # 动画
    "pagelet_game",  # 游戏
    "pagelet_amusement",  # 娱乐
]

pagelets_normal = [
    "pagelet_life",  # 生活
    "pagelet_tech",  # 科技
    "pagelet_dance",  # 舞蹈·偶像
    "pagelet_music",  # 音乐
    "pagelet_film",  # 影视
    "pagelet_fishpond",  # 鱼塘
    "pagelet_sport",  # 体育
]

pagelets = [
    "pagelet_header",  # 顶栏
    "pagelet_banner",  # banner
    "pagelet_navigation",  # 导航栏
    'pagelet_top_area',  # 置顶
    'pagelet_monkey_recommend',  # 猴子推荐
    'pagelet_live',  # 直播
    'pagelet_spring_festival',  # 春季节日活动
    'pagelet_list_banana',  # 香蕉榜
    "pagelet_douga",  # 动画
    "pagelet_game",  # 游戏
    "pagelet_amusement",  # 娱乐
    "pagelet_bangumi_list",  # 番剧
    "pagelet_life",  # 生活
    "pagelet_tech",  # 科技
    "pagelet_dance",  # 舞蹈·偶像
    "pagelet_music",  # 音乐
    "pagelet_film",  # 影视
    "pagelet_fishpond",  # 鱼塘
    "pagelet_sport",  # 体育
    'footer',  # 页脚
]

ChannelList = [
    {
        "children": [
            {
                "realms": [
                    {
                        "realmId": "18",
                        "introduction": "画的不好就继续画，还学人家瞎摸鱼！",
                        "realmName": "原创画作"
                    },
                    {
                        "realmId": "14",
                        "introduction": "桌面壁纸锁屏图集分享",
                        "realmName": "美图转载"
                    },
                    {
                        "realmId": "51",
                        "introduction": "相似度50%…60%…70%…80%…90%…100%！",
                        "realmName": "临摹练习"
                    }
                ],
                "name": "二次元画师",
                "channelType": 1,
                "channelId": "184"
            },
            {
                "realms": [
                    {
                        "realmId": "50",
                        "introduction": "爽字的50种写法",
                        "realmName": "爽文"
                    },
                    {
                        "realmId": "25",
                        "introduction": "独乐乐不如众乐乐。",
                        "realmName": "吐槽"
                    },
                    {
                        "realmId": "34",
                        "introduction": "又到一年剁手季...\n今年猴子连尾巴都剁掉啦！",
                        "realmName": "买买买！"
                    },
                    {
                        "realmId": "7",
                        "introduction": "可能是你最接近ACer平均水平的地方了。",
                        "realmName": "情感"
                    },
                    {
                        "realmId": "6",
                        "introduction": "手有面包，才能心怀梦想。",
                        "realmName": "工作"
                    },
                    {
                        "realmId": "17",
                        "introduction": "拉你的朋友们来AcFun,也别忘记和他们一起出门游玩！",
                        "realmName": "摄影游记"
                    },
                    {
                        "realmId": "1",
                        "introduction": "唯有美食与爱不可辜负！",
                        "realmName": "美食"
                    },
                    {
                        "realmId": "2",
                        "introduction": "总有一天，你也会有属于你的喵。",
                        "realmName": "萌宠"
                    },
                    {
                        "realmId": "49",
                        "introduction": "欢迎各位新人入驻AcFun",
                        "realmName": "新人报道"
                    }
                ],
                "name": "生活情感",
                "channelType": 1,
                "channelId": "73"
            },
            {
                "realms": [
                    {
                        "realmId": "5",
                        "introduction": "不知该去哪里寻乐子？遇事不决看这里！\nUP主各个都是人才，评论又有反白又有黑话，超喜欢在里面。",
                        "realmName": "杂谈"
                    },
                    {
                        "realmId": "22",
                        "introduction": "注意！本版不收录来自《杀人网球》的投稿！",
                        "realmName": "体育"
                    },
                    {
                        "realmId": "28",
                        "introduction": "每天都发生了点啥新鲜的？",
                        "realmName": "新闻资讯"
                    },
                    {
                        "realmId": "3",
                        "introduction": "每天都会诞生更多的经典好片和绝世烂片！把它们夸成一朵花或者喷得狗血淋头，是这个领域的主要职责！",
                        "realmName": "影视"
                    },
                    {
                        "realmId": "4",
                        "introduction": "这里有百家之言，这里鱼龙混杂，这里或许有你要的答案。",
                        "realmName": "自媒体专栏"
                    }
                ],
                "name": "综合",
                "channelType": 1,
                "channelId": "110"
            },
            {
                "realms": [
                    {
                        "realmId": "8",
                        "introduction": "No Game No Life",
                        "realmName": "游戏杂谈"
                    },
                    {
                        "realmId": "53",
                        "introduction": "当魂系体验遇到开放世界",
                        "realmName": "艾尔登法环"
                    },
                    {
                        "realmId": "52",
                        "introduction": "每个人都可以成为神",
                        "realmName": "原神"
                    },
                    {
                        "realmId": "11",
                        "introduction": "铸就你的决胜之道",
                        "realmName": "英雄联盟"
                    },
                    {
                        "realmId": "43",
                        "introduction": "还有谁要进本？",
                        "realmName": "暴雪游戏"
                    },
                    {
                        "realmId": "44",
                        "introduction": "禁止海豹！",
                        "realmName": "明日方舟"
                    },
                    {
                        "realmId": "45",
                        "introduction": "先来一发648！",
                        "realmName": "手机游戏"
                    },
                    {
                        "realmId": "46",
                        "introduction": "让我康康今天有哪些有趣的人在直憋。",
                        "realmName": "游戏主播"
                    },
                    {
                        "realmId": "47",
                        "introduction": "快手游戏、A站以及龙拳互娱3家联合发行全新二次元手游《命运神界》",
                        "realmName": "命运神界"
                    }
                ],
                "name": "游戏",
                "channelType": 1,
                "channelId": "164"
            },
            {
                "realms": [
                    {
                        "realmId": "13",
                        "introduction": "有关动漫的各种新闻、周边，八卦。",
                        "realmName": "动漫杂谈"
                    },
                    {
                        "realmId": "31",
                        "introduction": "只有塑料小人还有一点温暖！",
                        "realmName": "手办模玩"
                    },
                    {
                        "realmId": "48",
                        "introduction": "2020年4月新番《富豪刑警》子分区",
                        "realmName": "富豪刑警"
                    }
                ],
                "name": "动漫文化",
                "channelType": 1,
                "channelId": "74"
            },
            {
                "realms": [
                    {
                        "realmId": "15",
                        "introduction": "求求你们不要再分享奇怪的漫画啦！",
                        "realmName": "漫画"
                    },
                    {
                        "realmId": "23",
                        "introduction": "国漫，在路上！",
                        "realmName": "国漫·条漫"
                    },
                    {
                        "realmId": "16",
                        "introduction": "「以交往为前提而将与AC娘的一模一样的男孩子人体炼成之后，我竟然变成了她的仆人」",
                        "realmName": "文学"
                    }
                ],
                "name": "漫画文学",
                "channelType": 1,
                "channelId": "75"
            }
        ],
        "name": "文章",
        "channelType": 1,
        "channelId": "63"
    },
    {
        "children": [
            {
                "introduction": "以动画内容为主的短片",
                "name": "短片·手书·配音",
                "channelType": 2,
                "channelId": "190"
            },
            {
                "introduction": "布袋木偶戏与特摄片的相关衍生视频",
                "name": "特摄",
                "channelType": 2,
                "channelId": "99"
            },
            {
                "introduction": "漫展与COSPLAY、声优与各种官方延伸内容",
                "name": "COSPLAY·声优",
                "channelType": 2,
                "channelId": "133"
            },
            {
                "introduction": "动画番剧相关的预告、宣传等视频类资讯",
                "name": "动画资讯",
                "channelType": 2,
                "channelId": "159"
            },
            {
                "introduction": "在虚拟或现实世界进行偶像活动的虚拟形象",
                "name": "虚拟偶像",
                "channelType": 2,
                "channelId": "207"
            },
            {
                "introduction": "3D技术产生的二次元相关视频",
                "name": "MMD·3D",
                "channelType": 2,
                "channelId": "108"
            },
            {
                "introduction": "ACG相关的二次创作多媒体作品",
                "name": "MAD·AMV",
                "channelType": 2,
                "channelId": "107"
            },
            {
                "introduction": "动画相关视频，包含但不限于解说、盘点等",
                "name": "动画综合",
                "channelType": 2,
                "channelId": "106"
            },
            {
                "introduction": "番剧相关的二次创作相关视频",
                "name": "番剧二创",
                "channelType": 2,
                "channelId": "212"
            }
        ],
        "name": "动画",
        "channelType": 2,
        "channelId": "1"
    },
    {
        "children": [
            {
                "name": "治愈系",
                "channelType": 2,
                "channelId": "215"
            },
            {
                "introduction": "电子人声合成歌曲",
                "name": "Vocaloid",
                "channelType": 2,
                "channelId": "103"
            },
            {
                "introduction": "歌曲、纯音乐为创作主体及人声再演绎的作品",
                "name": "原创·翻唱",
                "channelType": 2,
                "channelId": "136"
            },
            {
                "introduction": "以乐器或器材演奏的作品",
                "name": "演奏·乐器",
                "channelType": 2,
                "channelId": "137"
            },
            {
                "introduction": "各类音乐作品以及音乐演出现场",
                "name": "综合音乐",
                "channelType": 2,
                "channelId": "139"
            },
            {
                "introduction": "以音乐分享为主并包括榜单及乐评的音乐集合",
                "name": "音乐选集·电台",
                "channelType": 2,
                "channelId": "185"
            }
        ],
        "name": "音乐",
        "channelType": 2,
        "channelId": "58"
    },
    {
        "children": [
            {
                "name": "颜值",
                "channelType": 2,
                "channelId": "218"
            },
            {
                "introduction": "偶像团体或个人的资讯，综艺，MV，LIVE等",
                "name": "偶像",
                "channelType": 2,
                "channelId": "129"
            },
            {
                "introduction": "原创编舞，振付翻跳的宅舞视频",
                "name": "宅舞",
                "channelType": 2,
                "channelId": "134"
            },
            {
                "introduction": "街舞，韩舞及其他类型的舞蹈视频",
                "name": "综合舞蹈",
                "channelType": 2,
                "channelId": "135"
            },
            {
                "name": "中国舞",
                "channelType": 2,
                "channelId": "208"
            }
        ],
        "name": "舞蹈·偶像",
        "channelType": 2,
        "channelId": "123"
    },
    {
        "children": [
            {
                "introduction": "王者荣耀相关视频",
                "name": "王者荣耀",
                "channelType": 2,
                "channelId": "214"
            },
            {
                "name": "和平精英",
                "channelType": 2,
                "channelId": "216"
            },
            {
                "introduction": "英雄联盟相关视频：CG，赛事战报，解说等",
                "name": "英雄联盟",
                "channelType": 2,
                "channelId": "85"
            },
            {
                "introduction": "我的世界Minecraft相关视频作品",
                "name": "我的世界",
                "channelType": 2,
                "channelId": "210"
            },
            {
                "introduction": "手机及其他移动端游戏为主要内容的视频",
                "name": "手机游戏",
                "channelType": 2,
                "channelId": "187"
            },
            {
                "name": "第五人格",
                "channelType": 2,
                "channelId": "217"
            },
            {
                "introduction": "除英雄联盟外，电子竞技游戏项目的相关视频",
                "name": "电子竞技",
                "channelType": 2,
                "channelId": "145"
            },
            {
                "introduction": "PC多人在线游戏为主要内容的视频",
                "name": "网络游戏",
                "channelType": 2,
                "channelId": "186"
            },
            {
                "introduction": "以PC单机、家用主机、掌机游戏为主的视频",
                "name": "主机单机",
                "channelType": 2,
                "channelId": "84"
            },
            {
                "introduction": "桌游、棋牌、卡牌对战游戏的相关视频",
                "name": "桌游卡牌",
                "channelType": 2,
                "channelId": "165"
            }
        ],
        "name": "游戏",
        "channelType": 2,
        "channelId": "59"
    },
    {
        "children": [
            {
                "introduction": "对素材音画进行处理，与BGM一致的同步感",
                "name": "鬼畜",
                "channelType": 2,
                "channelId": "87"
            },
            {
                "introduction": "娱乐圈动态及明星相关资讯",
                "name": "明星",
                "channelType": 2,
                "channelId": "188"
            },
            {
                "introduction": "搞笑有趣，土味沙雕",
                "name": "搞笑",
                "channelType": 2,
                "channelId": "206"
            }
        ],
        "name": "娱乐",
        "channelType": 2,
        "channelId": "60"
    },
    {
        "children": [
            {
                "introduction": "记录日常生活片段，分享生活经历或体验",
                "name": "生活日常",
                "channelType": 2,
                "channelId": "86"
            },
            {
                "introduction": "宠物生活记录及相关知识分享",
                "name": "萌宠",
                "channelType": 2,
                "channelId": "88"
            },
            {
                "introduction": "美食制作与鉴赏",
                "name": "美食",
                "channelType": 2,
                "channelId": "89"
            },
            {
                "introduction": "旅行地风光记录与分享、风土人情展示与介绍",
                "name": "旅行",
                "channelType": 2,
                "channelId": "204"
            },
            {
                "introduction": "妆发造型，护肤指南，穿搭交流等视频",
                "name": "美妆·造型",
                "channelType": 2,
                "channelId": "205"
            },
            {
                "introduction": "手工艺品及绘画作品的展示、制作与交流分享",
                "name": "手工·绘画",
                "channelType": 2,
                "channelId": "127"
            }
        ],
        "name": "生活",
        "channelType": 2,
        "channelId": "201"
    },
    {
        "children": [
            {
                "name": "手办模玩",
                "channelType": 2,
                "channelId": "209"
            },
            {
                "introduction": "前沿科技、手工DIY、模玩手办等视频",
                "name": "科技制造",
                "channelType": 2,
                "channelId": "90"
            },
            {
                "introduction": "3C数码产品、家电等相关视频",
                "name": "数码家电",
                "channelType": 2,
                "channelId": "91"
            },
            {
                "introduction": "汽车等轮式交通工具相关视频",
                "name": "汽车",
                "channelType": 2,
                "channelId": "122"
            },
            {
                "introduction": "电视广告，公益广告，各国创意广告等",
                "name": "广告",
                "channelType": 2,
                "channelId": "149"
            },
            {
                "introduction": "各类教程、公开课相关视频",
                "name": "演讲·公开课",
                "channelType": 2,
                "channelId": "151"
            },
            {
                "introduction": "科普、知识及人文性质相关视频",
                "name": "人文科普",
                "channelType": 2,
                "channelId": "189"
            }
        ],
        "name": "科技",
        "channelType": 2,
        "channelId": "70"
    },
    {
        "children": [
            {
                "name": "影视混剪",
                "channelType": 2,
                "channelId": "219"
            },
            {
                "introduction": "影剧综预告片，片花，采访",
                "name": "预告·花絮",
                "channelType": 2,
                "channelId": "192"
            },
            {
                "introduction": "电影解说、电影混剪、影视二创等",
                "name": "电影杂谈",
                "channelType": 2,
                "channelId": "193"
            },
            {
                "introduction": "电视剧解说，电视剧混剪，自制内容等。",
                "name": "追剧社",
                "channelType": 2,
                "channelId": "194"
            },
            {
                "introduction": "综艺相关所有短视频。",
                "name": "综艺Show",
                "channelType": 2,
                "channelId": "195"
            },
            {
                "introduction": "原创小型纪录片，短片解说等。",
                "name": "纪录片·短片",
                "channelType": 2,
                "channelId": "196"
            }
        ],
        "name": "影视",
        "channelType": 2,
        "channelId": "68"
    },
    {
        "children": [
            {
                "introduction": "跑酷、跳伞等极限运动及竞技赛车精彩剪辑",
                "name": "极限·竞速 ",
                "channelType": 2,
                "channelId": "93"
            },
            {
                "introduction": "足球相关视频，包括足球装备",
                "name": "足球",
                "channelType": 2,
                "channelId": "94"
            },
            {
                "introduction": "篮球相关视频，包括篮球装备",
                "name": "篮球",
                "channelType": 2,
                "channelId": "95"
            },
            {
                "introduction": "各类运动，运动装备等相关视频",
                "name": "综合体育",
                "channelType": 2,
                "channelId": "152"
            },
            {
                "introduction": "搏击，健身相关内容",
                "name": "搏击·健身",
                "channelType": 2,
                "channelId": "153"
            }
        ],
        "name": "体育",
        "channelType": 2,
        "channelId": "69"
    },
    {
        "children": [
            {
                "introduction": "剧场动画及动画电影",
                "name": "剧场动画",
                "channelType": 2,
                "channelId": "180"
            },
            {
                "introduction": "TV动画放送，包括OVA、OAD、SP特典等",
                "name": "TV动画",
                "channelType": 2,
                "channelId": "67"
            },
            {
                "introduction": "国产动画、动漫、有声漫画等国产动画类内容",
                "name": "国产动画",
                "channelType": 2,
                "channelId": "120"
            }
        ],
        "name": "番剧",
        "channelType": 2,
        "channelId": "155"
    },
    {
        "children": [
            {
                "introduction": "国内外热点与正能量！也欢迎个人脑洞类原创",
                "name": "新鲜事&正能量",
                "channelType": 2,
                "channelId": "132"
            },
            {
                "introduction": "真实历史故事，玄幻神话传说，这里都欢迎！",
                "name": "历史",
                "channelType": 2,
                "channelId": "131"
            },
            {
                "introduction": "机枪大炮、飞机坦克！F-22很帅，歼20更爱",
                "name": "国防军事",
                "channelType": 2,
                "channelId": "92"
            },
            {
                "introduction": "普法、破案、交通事故等普法安全相关视频",
                "name": "普法安全",
                "channelType": 2,
                "channelId": "183"
            }
        ],
        "name": "鱼塘",
        "channelType": 2,
        "channelId": "125"
    },
]
