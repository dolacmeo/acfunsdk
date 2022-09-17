# coding=utf-8
import httpx
from bs4 import BeautifulSoup as Bs
from acfunsdk.source import scheme, routes, apis
from .utils import url_complete

__author__ = 'dolacmeo'

AcFunWeixin_qr = "http://weixin.qq.com/r/6i7a3qnEcGEMKe29b3tu"
AcFunWeixin_qr_img = "https://cdnfile.aixifan.com/static/img/qrcode_e280b30.jpg"

AcFun_ico = "https://cdn.aixifan.com/ico/favicon.ico"
AcFun_logo = "https://ali-imgs.acfun.cn/kos/nlav10360/static/packageDownload/static/img/logo.e3f3277bac07179de334.png"
AcFun_login_bg = "https://static.yximgs.com/udata/pkg/acfun/loginbg.be7a2d2876ab48ed.png"
AcFun_danmaku_bg = [
    "https://ali-imgs.acfun.cn/kos/nlav10360/static/packageDownload/static/img/danmu-1.13b8f4cb7a790fdcfe19.png",
    "https://ali-imgs.acfun.cn/kos/nlav10360/static/packageDownload/static/img/danmu-2.7a0c666031b39fd1fa65.png",
]


class AcLink:

    def __init__(self, acer, url, title, container=None):
        self.acer = acer
        self.title = title
        self.url = url_complete(url)
        self.container = container

    def __repr__(self):
        show_link = f" >> {self.url}" if self.url else ""
        return f"AcLink({self.title}{show_link})"


class AcImage:

    def __init__(self, acer, src, url=None, name=None, container=None):
        self.acer = acer
        self.src = url_complete(src)
        self.name = name
        self.url = url_complete(url)
        self.container = container

    def __repr__(self):
        show_link = f" >> {self.url}" if self.url else ""
        return f"AcImg({self.name}[{self.src}]{show_link})"

    def link(self):
        return self.acer.get(self.url)


class AcHelp:
    banner = "https://ali-imgs.acfun.cn/kos/nlav10360/static/img/help-banner.740f1669.png"
    category = None
    hots = None

    def __init__(self):
        self.loading()

    def loading(self):
        tab_req = httpx.post(apis['feedback_tab'], json={"appType": "acfun_m"})
        tab_data = tab_req.json()
        assert tab_data.get("result") == 1
        for x in tab_data.get("tabFaqs", []):
            if x['tab'] == 'all':
                self.category = {str(c['id']): c for c in x['faqs']}
            if x['tab'] == 'common':
                self.hots = x

    def tab(self, parent_id: str):
        if parent_id not in self.category.keys():
            return None
        children_req = httpx.post(apis['feedback_children'],
                                  json={"appType": "acfun_m", "parentId": parent_id})
        children_data = children_req.json()
        assert children_data.get("result") == 1
        return children_data.get("children")

    def get(self, question_id: str):
        question_req = httpx.post(apis['feedback_question'],
                                  json={"appType": "acfun_m", "questionId": question_id})
        question_data = question_req.json()
        assert question_data.get("result") == 1
        return question_data


class AcInfo:
    about = {
        "url": "https://www.acfun.cn/info#page=about",
        "title": "关于AcFun弹幕视频网",
        "subtilte": "About Us",
        "content": [
            "AcFun弹幕视频网隶属于北京弹幕网络科技有限公司，是中国最具影响力的弹幕视频平台，"
            "也是全球最早上线的弹幕视频网站之一。“AcFun”原取意于“Anime Comic Fun”。"
            "自2007年6月6日成立以来，AcFun历经几年努力，从最初单一的视频站发展为现在的综合性弹幕视频网站，"
            "目前已是国内弹幕视频行业的领军品牌。",
            "AcFun从创立之初就坚持以“天下漫友是一家”为主旨，以“认真你就输了”为文化导向，倡导轻松欢快的亚文化。"
            "在几年中吸引了无数深爱宅文化的观众，也诞生了难以计数的知名原创视频作者。"
            "几年中由AcFun推广的无数优秀视频作品，深刻影响和改变了众多宅文化爱好者，"
            "它们中的大多数现已经成为网络经典。",
            "让更多人融入到弹幕视频的互动中去，让更多人理解宅文化的魅力所在，这就是几年来AcFun一直孜孜不倦追求的目标。"
            "随着时代变迁，AcFun也在不断进步和革新，以崭新的面貌，为所有热爱宅文化的观众们带来更完美的视听享受。",
        ]
    }
    contact = {
        "url": "https://www.acfun.cn/info#page=contact",
        "title": "联系我们",
        "subtilte": "Contact Us",
    }
    agreement = {
        "url": "https://www.acfun.cn/info#page=agreement",
        "title": "AcFun软件许可用户服务协议",
        "subtilte": "Agreement",
    }
    privacy = {
        "url": "https://www.acfun.cn/info#page=privacy",
        "title": "隐私权保护政策",
        "subtilte": "privacy",
    }
    children_privacy = {
        "url": "https://www.acfun.cn/info#page=children-privacy",
        "title": "儿童个人信息保护规则及监护人须知",
        "subtilte": "Children's Privacy",
    }
    children_guard = {
        "url": "https://www.acfun.cn/info#page=children-guard",
        "title": "儿童守护协议及监护人须知",
        "subtilte": "Children's Guard",
    }
    experience = {
        "url": "https://www.acfun.cn/info#page=experience",
        "title": "等级系统说明",
        "subtilte": "Experience System",
        "content": [
            "https://cdn.aixifan.com/dotnet/20130418/project/info/style/image/experience-1.jpg",
            "https://cdn.aixifan.com/dotnet/20130418/project/info/style/image/experience-2-2.jpg",
            "https://cdn.aixifan.com/dotnet/20130418/project/info/style/image/experience-3.png"
        ]
    }
    limit = {
        "url": "https://www.acfun.cn/info#page=limit",
        "title": "会员特权说明",
        "subtilte": "Experience System",
        "content": [
            "https://ali-imgs.acfun.cn/udata/pkg/acfun/member_level_desc.png"
        ]
    }


class AcReport:
    url = "https://www.acfun.cn/infringementreport"
    complaint_doc = "https://cdn.aixifan.com/downloads/AcFun%E4%B8%BE%E6%8A%A5%E7%94%B3%E8%AF%89%E8%A1%A8.doc"
    email = "ac-report@kuaishou.com"

    @staticmethod
    def submit(url: str, rid: str, rtype: str, uid: str, crime: str, proof: str, description: str):
        assert int(rtype) in [1, 2, 3, 4, 5, 6, 8, 10]
        crimes = ['色情', '血腥', '暴力', '猎奇', '政治', '辱骂', '广告', '挖坟', '剧透', '其他',
                  '话题不符', '少儿不宜', '未成年不良信息']
        assert int(crime) in range(1, len(crimes) + 1)
        assert uid.isdigit()
        assert len(url) >= 5
        assert len(proof) >= 5
        assert len(description) >= 5
        form = {
            "url": url,
            "resourceId": rid,
            "resourceType": rtype,
            "defendantUserId": uid,
            "crime": crime,
            "proof": proof,
            "description": description,
        }
        api_req = httpx.post(apis['report'], data=form)
        return api_req.json().get("result") == 0

    @staticmethod
    def feedback(title: str, content: str, tel: str):
        assert len(title) >= 5
        assert len(content) >= 5
        assert len(tel) == 11
        form = {"title": title, "content": content, "tel": tel}
        api_req = httpx.post(apis['feedback'], data=form)
        return api_req.json().get("result") == 0


class AcAcademy:
    url = "https://member.acfun.cn/academy"
    banner = "https://static.yximgs.com/udata/pkg/acfun-fe/up.cd94ec8275ced105.png"
    background = "https://tx2.a.kwimgs.com/udata/pkg/acfun/bg.e4bb289f.png"
    question_image = "https://tx2.a.kwimgs.com/udata/pkg/acfun/qadayi.b87cd018.png"
    answer_image = "https://tx2.a.kwimgs.com/udata/pkg/acfun/pc.5b40a899.png"

    acer_class = [
        {
            "resourceType": 2,
            "resourceId": 11772415,
            "title": "「萌新UP入门教程」第一期：迈出创作之路第一步",
            "coverUrl": "https://imgs.aixifan.com/voUp9bcRrP-yaURNn-FNZZRb-JvAJVj-NBZ3Un.jpg",
        },
        {
            "resourceType": 2,
            "resourceId": 11808491,
            "title": "「萌新UP入门教程」第二期：如何选择分区？",
            "coverUrl": "https://imgs.aixifan.com/S6aSTGHCo0-ny2mqe-aiuaM3-BZfMna-ArAVbi.jpg",
        },
        {
            "resourceType": 2,
            "resourceId": 11836309,
            "title": "「萌新UP入门教程」第三期：用户中心内有乾坤",
            "coverUrl": "https://imgs.aixifan.com/kicNLtKNf1-7B73Az-EbUjYj-2eYbYv-BBVnYb.jpg",
        },
        {
            "resourceType": 2,
            "resourceId": 11836337,
            "title": "「萌新UP入门教程」第四期：香蕉的秘密",
            "coverUrl": "https://imgs.aixifan.com/JxHjqEDGrs-BBRf2m-InEvqu-iANFBz-bqa6ba.jpg",
        },
        {
            "resourceType": 2,
            "resourceId": 11836377,
            "title": "「萌新UP入门教程」第五期：阿普学院是什么组织？",
            "coverUrl": "https://imgs.aixifan.com/YJaQxr4JHu-Q7jyE3-32y6bm-yyEbEb-E7viie.jpg",
        },
        {
            "resourceType": 2,
            "resourceId": 11836385,
            "title": "「萌新UP入门教程」第六期：审核二三事",
            "coverUrl": "https://imgs.aixifan.com/V5eSIu1M7m-aaEJnu-UBn67r-AvIryu-3URjqq.jpg",
        },
    ]

    @staticmethod
    def acer_teacher():
        form = {"courseType": "2", "pageSize": 40, "page": 1}
        api_req = httpx.post(apis['academy_tea'], data=form)
        api_data = api_req.json()
        return api_data.get("teacherList")


class AcDownload:
    _app_page_raw = None

    def __init__(self, acer):
        self.acer = acer

    def _app_page_obj(self):
        if self._app_page_raw is None:
            page_req = self.acer.client.get(routes['app'])
            self._app_page_raw = Bs(page_req.text, 'lxml')
        return self._app_page_raw

    def emots(self):
        urls = list()
        emot_page = self.acer.client.get(routes['emot'])
        emot_obj = Bs(emot_page.text, 'lxml')
        for item in emot_obj.select('.emot-download'):
            title = item.select_one(".emot-name").text
            url = item.select_one("a.download-btn").attrs['href']
            details = item.select_one(".emot-detail-top")
            images = list()
            if details:
                for img in details.select('img'):
                    images.append(f"{scheme}:{img.attrs['src']}")
            urls.append({'title': title, 'url': f"{scheme}:{url}", 'details': images})
        return urls

    def Android_apk(self):
        api_req = self.acer.client.get(apis['app_download'])
        api_data = api_req.json()
        return api_data.get('url')

    def iOS_link(self):
        ios_link = self._app_page_obj().select_one(".app-info .download a.ios")
        return ios_link.attrs['href']

    def LiveMate_win(self):
        win_link = self._app_page_obj().select_one('.zbbl-info .download a.win')
        return win_link.attrs['href']

    def VirtualView_win(self):
        win_link = self._app_page_obj().select_one('.mbzs-info .download a.win')
        psd_link = self._app_page_obj().select_one('.mbzs-info .dis a.download-psd')
        return win_link.attrs['href'], psd_link.attrs['href']

    def FaceCatcher_win(self):
        api_res = self.acer.client.post(apis['face_catcher'], headers={
            "referer": "https://www.acfun.cn/face-catcher",
            "origin": "https://www.acfun.cn"
        })
        api_data = api_res.json()
        return api_data['downloadUrl'], api_data['psdUrl']

    def emot_zips(self):
        urls = list()
        api_res = self.acer.client.post(apis['emot'], headers={
            "referer": "https://www.acfun.cn/info/",
            "origin": "https://www.acfun.cn"
        })
        api_data = api_res.json()
        for em in api_data['emotionPackageList']:
            if em['downloadUrl']:
                urls.append({'url': em['downloadUrl'], 'filename': f"{em['name']}.zip"})
        return urls
