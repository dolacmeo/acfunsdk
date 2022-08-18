# coding=utf-8
import os
import json
from uuid import uuid4
from urllib.parse import urlparse
from .page.utils import downloader
from .source import apis
from jinja2 import PackageLoader, Environment

__author__ = 'dolacmeo'

# env = Environment(loader=PackageLoader('acfun', 'templates'))  # 创建一个包加载器对象
# template = env.get_template('demo.html')  # 获取一个模板文件
# ttt = template.render(hello='world')
# print(ttt)


class AcSaver:

    def __init__(self, acer, ac_obj, dest_path=None):
        self.acer = acer
        self.ac_obj = ac_obj
        self.dest_path = dest_path or os.getcwd()
        if not os.path.isdir(self.dest_path):
            os.makedirs(self.dest_path, exist_ok=True)
        self.cdns = self.acer.client.post(apis['cdn_domain'], headers={
            "referer": "https://www.acfun.cn"}).json().get('domain')

    def _download(self, src_url: str, fname: [str, None] = None, ex_dir: [list, None] = None):
        save_path = self.dest_path if ex_dir is None else os.path.join(self.dest_path, *ex_dir)
        return downloader(self.acer.client, src_url, fname, save_path)

    def _save_data(self, data: [dict, list, str], fname: str, ex_dir: [list, None] = None):
        if isinstance(data, (dict, list)):
            data = json.dumps(data, separators=(',', ':'))
        elif isinstance(data, str):
            pass
        else:
            return False
        save_path = self.dest_path if ex_dir is None else os.path.join(self.dest_path, *ex_dir)
        file_path = os.path.join(save_path, fname)
        if not file_path.endswith('.json'):
            file_path += '.json'
        with open(file_path, 'w') as save_file:
            save_file.write(data)
        return os.path.exists(file_path)

    def _save_images(self, src_url: str, fname: [str, None] = None, ex_dir: [list, None] = None):
        src_uu = urlparse(src_url)
        if fname is None:
            fname = src_uu.path.split('/')[-1]
            if src_url.startswith("https://www.acfun.cn/imageProxy?"):
                fname = uuid4().hex.upper()
            # elif src_uu.netloc in self.cdns:
            #     fname = src_uu.path.split('/')[-1]
        return self._download(src_url, fname, ex_dir)

    def _save_member(self, ids: list):
        done = list()
        member_dir = os.path.join(self.dest_path, 'member')
        for uid in ids:
            user_req = self.acer.client.get(apis['userInfo'], params=dict(userId=uid))
            user_data = user_req.json()
            profile = user_data.get('profile')
            user_json = os.path.join(member_dir, f"{uid}.json")
            with open(user_json, 'w') as uid_file:
                json.dump(profile, uid_file, separators=(',', ':'))
            avatar = urlparse(profile['headUrl'])
            avatar_path = self._save_images(f"{avatar.scheme}://{avatar.netloc}{avatar.path}", uid, ['member'])
            if avatar_path is None:
                continue
            if os.path.isfile(user_json) and os.path.isfile(avatar_path):
                done.append(uid)
        return done

    def _save_comment(self):
        pass

    def _save_damaku(self):
        pass


class ArticleSaver(AcSaver):

    def _save_content(self):
        pass

    pass


class MomentSaver(AcSaver):

    def _save_content(self):
        pass

    pass


class VideoSaver(AcSaver):

    def _save_video(self):
        pass

    pass


class BangumiSaver(AcSaver):

    def _save_season(self):
        pass

    def _save_episode(self):
        pass

    pass


class LiveSaver(AcSaver):
    pass
