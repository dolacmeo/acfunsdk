# coding=utf-8
import os
import json
import js2py
from bs4 import BeautifulSoup as Bs
from acfun.source import routes
from acfun.page.utils import ms2time, get_channel_info, get_page_pagelets, AcDanmaku
from acfun.libs.you_get.extractors.acfun import download as you_get_download

__author__ = 'dolacmeo'


class AcVideo:
    ac_num = None
    page_obj = None
    page_pagelets = []
    video_data = dict()
    vid = None
    resourceType = 9

    def __init__(self, acer, ac_num: [str, int], video_data: [dict, None] = None):
        if isinstance(ac_num, str) and ac_num.startswith('ac'):
            ac_num = ac_num[2:]
        self.ac_num = str(ac_num)
        self.referer = f"{routes['video']}{ac_num}"
        self.acer = acer
        if isinstance(video_data, dict):
            self.video_data = video_data
        self.loading()
        if "_" in self.ac_num:
            self.set_video(int(self.ac_num.split('_')[-1]))

    def __repr__(self):
        title = self.video_data.get('title', "")
        user_name = self.video_data.get('user', {}).get('name', "") or self.video_data.get('user', {}).get('id', "")
        user_txt = "" if len(user_name) == 0 else f" @{user_name}"
        duration = self.video_data.get('durationMillis', 0)
        duration_txt = "" if duration == 0 else f"[{ms2time(duration)}]"
        return f"AcVideo([ac{self.ac_num}]{duration_txt}{title}{user_txt})".encode(errors='replace').decode()

    def loading(self):
        req = self.acer.client.get(routes['video'] + self.ac_num)
        self.page_obj = Bs(req.text, 'lxml')
        js_code = self.page_obj.select_one("#pagelet_newheader").find_next_sibling("script").text.strip().split('\n')[0]
        self.video_data = js2py.eval_js(js_code).to_dict()
        self.video_data.update(get_channel_info(req.text))
        self.vid = self.video_data.get("currentVideoId")
        self.page_pagelets = get_page_pagelets(self.page_obj)

    @property
    def video_list(self):
        return self.video_data.get('videoList', [])

    def set_video(self, num=1):
        if num > len(self.video_list):
            return False
        self.vid = self.video_list[num - 1]['id']
        self.video_data.update({'currentVideoId': self.vid})
        return True

    def download(self, num=1):
        self.set_video(num)
        v_num = f"_{num}" if num > 1 else ""
        video_download_path = os.path.join(self.acer.DOWNLOAD_PATH, 'video')
        you_get_download(self.referer + v_num, output_dir=video_download_path, merge=True)
        with open(os.path.join(video_download_path, f"ac{self.ac_num}.json"), 'w') as jfile:
            json.dump(self.video_data, jfile)
            jfile.close()
        return True

    def up(self):
        return self.acer.AcUp(self.video_data.get('user', {}))

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
