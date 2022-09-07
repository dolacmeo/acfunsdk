# coding=utf-8
import os
import json
from bs4 import BeautifulSoup as Bs
from acfun.source import routes, apis
from acfun.page.utils import ms2time, \
    get_channel_info, get_page_pagelets, acfun_video_downloader, \
    AcDanmaku, match1
from acfun.saver import VideoSaver

__author__ = 'dolacmeo'


class AcVideo:
    ac_num = None
    page_obj = None
    page_pagelets = []
    video_data = dict()
    vid = None
    resourceType = 9
    is_404 = False

    def __init__(self, acer, ac_num: [str, int], video_data: [dict, None] = None):
        if isinstance(ac_num, str) and ac_num.startswith('ac'):
            ac_num = ac_num[2:]
        self.ac_num = str(ac_num)
        self.part_num = 1
        self.acer = acer
        if isinstance(video_data, dict):
            self.video_data = video_data
        if "_" in self.ac_num:
            self.ac_num, self.part_num = self.ac_num.split('_')
        self.loading()

    @property
    def referer(self):
        if int(self.part_num) == 1:
            return f"{routes['video']}{self.ac_num}"
        return f"{routes['video']}{self.ac_num}_{self.part_num}"

    @property
    def share_url(self):
        return self.referer

    @property
    def mobile_url(self):
        return f"https://scan.acfun.cn/vd/{self.ac_num}"

    def __repr__(self):
        if self.is_404:
            return f"AcVideo([ac{self.ac_num}]咦？世界线变动了。看看其他内容吧~)"
        title = self.video_data.get('title', "")
        title = title if len(title) < 28 else title[:27] + ".."
        user_name = self.video_data.get('user', {}).get('name', "") or self.video_data.get('user', {}).get('id', "")
        user_txt = "" if len(user_name) == 0 else f" @{user_name}"
        duration = self.video_data.get('durationMillis', 0)
        duration_txt = "" if duration == 0 else f"[{ms2time(duration)}]"
        return f"AcVideo([ac{self.ac_num}]{duration_txt}{title}{user_txt})".encode(errors='replace').decode()

    def loading(self):
        req = self.acer.client.get(self.referer)
        self.is_404 = req.status_code == 404
        if self.is_404:
            return False
        self.page_obj = Bs(req.text, 'lxml')
        json_text = match1(req.text, r"(?s)videoInfo\s*=\s*(\{.*?\});")
        self.video_data = json.loads(json_text)
        self.video_data.update(get_channel_info(req.text))
        self.vid = self.video_data.get("currentVideoId")
        self.page_pagelets = get_page_pagelets(self.page_obj)
        staff_data = self.staff()
        if staff_data is not None:
            self.video_data['staffInfos'] = staff_data.get('staffInfos')
            self.video_data['upInfo'] = staff_data.get('upInfo')

    def saver(self, dest_path=None):
        return VideoSaver(self.acer, self, dest_path)

    @property
    def video_list(self):
        return self.video_data.get('videoList', [])

    def set_video(self, num=1):
        assert num <= len(self.video_list)
        self.part_num = num
        self.loading()
        return True

    def download(self, num=1, quality=None):
        self.set_video(num)
        video_download_path = os.path.join(self.acer.BASE_PATH, f"ac{self.ac_num}")
        saved = acfun_video_downloader(self.acer.client, self.video_data, video_download_path, quality)
        if saved is False:
            return False
        with open(os.path.join(video_download_path, f"ac{self.ac_num}.json"), 'w') as jfile:
            json.dump(self.video_data, jfile)
        return True

    def up(self):
        return self.acer.AcUp(self.video_data.get('user', {}))

    def staff(self):
        if self.video_data.get('staffContribute') is not True:
            return None
        form_data = {"resourceId": self.ac_num, "resourceType": 2}
        api_req = self.acer.client.post(apis['getStaff'], data=form_data)
        api_data = api_req.json()
        return api_data

    def danmaku(self):
        return AcDanmaku(self.acer, self.video_data)

    def comment(self):
        return self.acer.AcComment(self.ac_num, 3, self.referer)

    def like(self):
        return self.acer.like(self.ac_num, 2)

    def like_cancel(self):
        return self.acer.like_cancel(self.ac_num, 2)

    def favorite_add(self, folder_id: [str, None] = None):
        return self.acer.favourite.add(self.ac_num, self.resourceType, folder_id)

    def favorite_cancel(self, folder_id: [str, None] = None):
        return self.acer.favourite.cancel(self.ac_num, self.resourceType, folder_id)

    def banana(self, count: int):
        return self.acer.throw_banana(self.ac_num, 2, count)

    # 一键奥里给！
    def aoligei(self, danmu: bool = False, comment: bool = False):
        """ 赞 藏 蕉 弹 评 """
        """ 👍 🔖 🍌 🌠 💬 """
        print(self.like())  # 👍 点赞
        print(self.favorite_add())  # 🔖 收藏
        print(self.banana(5))  # 🍌 投蕉
        if danmu is True:  # 🌠 发弹幕
            self.danmaku().add("棒棒棒~加油哦~", 0)
        if comment is True:  # 💬 留言
            self.comment().add('<p><font color="#ff0000">棒棒棒~加油哦~</font></p>'
                               '<p><font color="#c4bd97">from  acfunSDK</font></p>')
        print(f" 赞 藏 蕉 弹 评 \n 👍 🔖 🍌 🌠 💬 \n 分享：{self.referer}?shareUid={self.acer.uid}")
        return True
