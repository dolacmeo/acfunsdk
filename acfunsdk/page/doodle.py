# coding=utf-8
from .utils import json, httpx, Bs
from .utils import AcSource, match1

__author__ = 'dolacmeo'


class AcDoodle:
    doodle_data = None
    doodle_title = None
    doodle_video = list()
    doodle_bg = list()
    doodle_image = list()
    doodle_text = list()
    doodle_button = list()
    doodle_vote = None
    page_obj = None

    def __init__(self, acer, doodle_id: str):
        self.acer = acer
        self.doodle_id = doodle_id
        if self.doodle_id.endswith(".html"):
            self.doodle_id = self.doodle_id[:-5]
        self.loading()

    def __repr__(self):
        return f"AcDoodle({self.doodle_title})"

    @property
    def referer(self):
        return f"{AcSource.routes['doodle']}{self.doodle_id}.html"

    def loading(self):
        page_req = httpx.get(self.referer)
        self.page_obj = Bs(page_req.text, 'lxml')
        self.doodle_title = self.page_obj.select_one('title').text
        json_text = match1(page_req.text, r"(?s)__schema__\s*=\s*'(\{.*?\})';")
        self.doodle_data = json.loads(json_text.replace(r'\\"', r'\"'))
        root_id = self.doodle_data['app']['data']['rootContainer']
        main_block = None
        for item_id in self.doodle_data[root_id]['data']['children']:
            if self.doodle_data[item_id]['elementInfo']['label'] == 'Block':
                main_block = item_id
                block_bg = self.doodle_data[item_id]['values'].get("styles.background-image", {}).get("value")
                if block_bg:
                    self.doodle_bg.append(block_bg)
                break
        if main_block is None:
            return None
        for k in self.doodle_data[main_block]['data']['children']:
            ele = self.doodle_data[k]
            ele_name = ele['elementInfo']['label']
            ele_bg = ele['values'].get("styles.background-image", {}).get("value")
            if ele_bg:
                self.doodle_bg.append(ele_bg)
            if ele_name == 'PcAcfunVideo':
                self.doodle_video.append({
                    "raw": ele,
                    "name": ele_name,
                    "videoId": ele['values']['vid']['value'],
                    "resourceId": ele['values']['resourceId']['value'],
                })
            elif ele_name == 'PcCommonImage':
                self.doodle_image.append({
                    "raw": ele,
                    "name": ele['editorData']['name'],
                    "src": ele['values']['src']['value'],
                })
            elif ele_name == 'PcCommonText':
                self.doodle_text.append({
                    "raw": ele,
                    "name": ele['editorData']['name'],
                    "text": ele['values']['text']['value'],
                })
            elif ele_name == 'PcCommonButton':
                self.doodle_button.append({
                    "raw": ele,
                    "name": ele['editorData']['name'],
                    "url": ele['values']['url']['value'],
                    "action": ele['values']['action']['value'],
                })
            elif ele_name == 'PcAcfunVote':
                self.doodle_vote = {
                    "raw": ele,
                    "name": ele['editorData']['name'],
                    "voteId": ele['values']['voteId']['value'],
                    "voteToken": ele['values']['voteToken']['value'],
                }
        self.doodle_image = sorted(self.doodle_image, key=lambda x: x['raw']['values']['styles.offset-y']['value'])

    def vote_data(self):
        if self.doodle_vote is None:
            return None
        data = {
            "token": self.doodle_vote['voteToken'],
            "tags": "",
            "page": 1,
            "count": 10,
            "sort": 1,
            "title": ""
        }
        api_req = self.acer.client.post(AcSource.apis['doodle_vote'], json=data)
        api_data = api_req.json()
        assert api_data.get("result") == 1
        return api_data

    def comment_feed(self, pcursor: [str, None] = None):
        form = {
            "objectId": f"{self.doodle_id}",
            "pageSize": "10",
            "subBiz": "jimu",
            "kpf": "PC_WEB",
            "kpn": "ACFUN_APP",
            "pcursor": pcursor or "",
        }
        api_req = self.acer.client.post(AcSource.apis['doodle_comment'], data=form)
        api_data = api_req.json()
        assert api_data.get("result") == 1
        return api_data


if __name__ == '__main__':
    pass
