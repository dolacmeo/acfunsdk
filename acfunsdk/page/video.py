# coding=utf-8
from .utils import parse
from .utils import AcSource, AcDetail, not_404, get_channel_info


__author__ = 'dolacmeo'


class AcVideo(AcDetail):

    def __init__(self, acer, rid: [str, int]):
        if isinstance(rid, str) and rid.startswith('ac'):
            rid = rid[2:]
            if "_" in rid:
                rid, _ = map(int, rid.split('_'))
        super().__init__(acer, 2, rid)

    def _staff(self):
        if self.raw_data.get('staffContribute') is not True:
            return None
        form_data = {"resourceId": self.resource_id, "resourceType": self.resource_type}
        api_req = self.acer.client.post(AcSource.apis['getStaff'], data=form_data)
        api_data = api_req.json()
        return api_data

    def loading_more(self):
        self.raw_data.update(get_channel_info(self.page_text))
        staff_data = self._staff()
        if staff_data is not None:
            self.raw_data['staffInfos'] = staff_data.get('staffInfos')
            self.raw_data['upInfo'] = staff_data.get('upInfo')

    def video(self, index: int = 0):
        assert index in range(len(self.video_list))
        vid = self.video_list[index]
        ends = "" if index == 0 else f"_{index + 1}"
        title = "" if len(self.video_list) == 1 else vid['title']
        return self.get_video(vid['id'], title, f"{self.referer}{ends}")

    @property
    def mobile_url(self):
        return f"https://scan.acfun.cn/vd/{self.resource_id}"

    @property
    def mobile_qrcode(self):
        parma = {
            "content": self.mobile_url,
            "contentType": "URL",
            "toShortUrl": False,
            "width": 100,
            "height": 100
        }
        return f"{AcSource.apis['qrcode']}?{parse.urlencode(parma)}"

    @property
    @not_404
    def video_list(self):
        return self.raw_data.get('videoList', [])

    @property
    def title(self):
        if self.is_404:
            return self._msg['404']
        return self.raw_data.get('title', "")

    def __repr__(self):
        if self.is_404:
            return f"AcVideo([ac{self.resource_id}]咦？世界线变动了。看看其他内容吧~)"
        title = self.title if len(self.title) < 28 else self.title[:27] + ".."
        user_name = self._up_name or self._up_uid
        user_txt = "" if len(user_name) == 0 else f" @{user_name}"
        return f"AcVideo([ac{self.resource_id}]{title}{user_txt})".encode(errors='replace').decode()
