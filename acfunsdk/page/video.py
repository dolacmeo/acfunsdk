# coding=utf-8
from acfunsdk.source import routes, apis
from acfunsdk.page.utils import AcDetail, not_404, ms2time, get_channel_info

__author__ = 'dolacmeo'


class AcVideo(AcDetail):
    vid = None

    def __init__(self, acer, rid: [str, int]):
        if isinstance(rid, str) and rid.startswith('ac'):
            rid = rid[2:]
        self.resource_id = str(rid)
        self.part_num = 1
        if "_" in self.resource_id:
            self.resource_id, self.part_num = self.resource_id.split('_')
        self.acer = acer
        super().__init__(acer, 2, self.resource_id)

    @property
    def share_url(self):
        return self.referer

    @property
    def mobile_url(self):
        return f"https://scan.acfun.cn/vd/{self.resource_id}"

    @property
    def title(self):
        return self.raw_data.get('title', "")

    def __repr__(self):
        if self.is_404:
            return f"AcVideo([ac{self.resource_id}]咦？世界线变动了。看看其他内容吧~)"
        title = self.title if len(self.title) < 28 else self.title[:27] + ".."
        user_name = self.up_name or self.up_uid
        user_txt = "" if len(user_name) == 0 else f" @{user_name}"
        duration = self.raw_data.get('durationMillis', 0)
        duration_txt = "" if duration == 0 else f"[{ms2time(duration)}]"
        return f"AcVideo([ac{self.resource_id}]{duration_txt}{title}{user_txt})".encode(errors='replace').decode()

    def loading_more(self):
        self.raw_data.update(get_channel_info(self.page_text))
        self.vid = self.raw_data.get("currentVideoId")
        staff_data = self.staff()
        if staff_data is not None:
            self.raw_data['staffInfos'] = staff_data.get('staffInfos')
            self.raw_data['upInfo'] = staff_data.get('upInfo')

    @not_404
    @property
    def video_list(self):
        return self.raw_data.get('videoList', [])

    @not_404
    def video_scenes(self):
        form_data = {"resourceId": self.resource_id, "resourceType": self.resource_type,
                     "videoId": self.raw_data.get('currentVideoId')}
        api_req = self.acer.client.post(apis['video_scenes'], data=form_data)
        api_data = api_req.json()
        if api_data.get('result') != 0:
            return None
        if api_data.get("spriteVtt") is None:
            return None
        pos_data = list()
        sprite_data = api_data.get("spriteVtt", "").split("\n\n")[1:]
        sprite_img = sprite_data[0].split("\n")[1].split("#")[0]
        for line in sprite_data:
            pos, img_url = line.split("\n")
            pos_s, pos_e = pos.split(" --> ")
            _, xywh = img_url.split("#xywh=")
            pos_data.append([pos_s, pos_e, xywh])
        return {"sprite_image": sprite_img, "pos": pos_data}

    @not_404
    def video_hotspot(self):
        form_data = {"resourceId": self.resource_id, "resourceType": self.resource_type}
        api_req = self.acer.client.post(apis['video_hotspot'], data=form_data)
        api_data = api_req.json()
        if api_data.get('result') != 0:
            return None
        return api_data.get("hotSpotDistribution")

    @not_404
    def set_video(self, num=1):
        assert num <= len(self.video_list)
        self.part_num = num
        self.loading_more()
        return True

    @not_404
    def get_ksPlayJson(self, video_id: [str, int, None] = None):
        param = {"resourceId": self.resource_id, "resourceType": 2}
        if video_id is not None:
            param['videoId'] = video_id
        api_req = self.acer.client.get(apis['video_ksplay'], params=param)
        api_data = api_req.json()
        if api_data.get('result') != 0:
            return None
        return api_data.get("playInfo")

    @not_404
    def staff(self):
        if self.raw_data.get('staffContribute') is not True:
            return None
        form_data = {"resourceId": self.resource_id, "resourceType": self.resource_type}
        api_req = self.acer.client.post(apis['getStaff'], data=form_data)
        api_data = api_req.json()
        return api_data

    @not_404
    def favorite_add(self, folder_id: [str, None] = None):
        return self.acer.favourite.add(self.resource_type, self.resource_id, folder_id)

    @not_404
    def favorite_cancel(self, folder_id: [str, None] = None):
        return self.acer.favourite.cancel(self.resource_type, self.resource_id, folder_id)

    # 一键奥里给！
    @not_404
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
