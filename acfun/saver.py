# coding=utf-8
import os
import json
import time
import arrow
import shutil
from uuid import uuid4
from urllib.parse import urlparse
from bs4 import BeautifulSoup as Bs
from .page.utils import downloader
from .source import routes, apis
from jinja2 import PackageLoader, Environment
from acfun.libs.you_get.extractors.acfun import download as you_get_download

__author__ = 'dolacmeo'


def unix2datestr(t):
    return arrow.get(t, tzinfo="Asia/Shanghai").format('YYYY-MM-DD HH:mm:ss')


class AcSaver:
    templates = Environment(loader=PackageLoader('acfun', 'templates'))
    templates.filters['unix2datestr'] = unix2datestr
    obj2folder = {
        "AcArticle": "article",
        "AcMoment": "moment",
        "AcVideo": "video",
        "AcBangumi": "bangumi",
        "AcLive": "live",
        "AcUp": "member"
    }

    def __init__(self, acer, ac_obj, dest_path=None):
        self.acer = acer
        self.ac_obj = ac_obj
        self.dest_path = dest_path or os.path.join(os.getcwd(), 'download')
        self.folder_name = self.obj2folder.get(self.ac_obj.__class__.__name__, "else")
        if not os.path.isdir(self.dest_path):
            os.makedirs(self.dest_path, exist_ok=True)
        self.cdns = self.acer.client.post(apis['cdn_domain'], headers={
            "referer": "https://www.acfun.cn"}).json().get('domain')

    def _setup_folder(self):
        folder_path = os.path.join(self.dest_path, self.folder_name, f"ac{self.ac_obj.ac_num}")
        if self.folder_name in ["article", "moment", "video", "bangumi"]:
            os.makedirs(os.path.join(folder_path, 'imgs'), exist_ok=True)
        else:
            os.makedirs(folder_path, exist_ok=True)
        return folder_path

    def _renew_folder(self, abs_path: str):
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        if os.path.isdir(abs_path):
            shutil.rmtree(abs_path, True)
        os.makedirs(abs_path)

    def _download(self, src_url: str, fname: [str, None] = None, ex_dir: [list, None] = None):
        save_path = self.dest_path if ex_dir is None else os.path.join(self.dest_path, *ex_dir)
        return downloader(self.acer.client, src_url, fname, save_path, display=False)

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
            new_avatar_path = "_".join([os.path.splitext(avatar_path)[0], 'avatar'])
            shutil.move(avatar_path, new_avatar_path)
            if avatar_path is None:
                continue
            if os.path.isfile(user_json) and os.path.isfile(new_avatar_path):
                done.append(uid)
        return done

    def _json_saver(self, data: dict, filename: str, dest_path=None):
        folder_path = self._setup_folder()
        json_path = os.path.join(self.dest_path, folder_path, filename)
        if dest_path is not None:
            json_path = os.path.join(dest_path, filename)
        with open(json_path, 'w') as json_file:
            json.dump(data, json_file, separators=(',', ':'))
        return os.path.isfile(json_path)

    def _save_comment(self):
        comment_obj = self.ac_obj.comment()
        comment_obj.get_all_comment()
        comment_data = {
            "hotComments": comment_obj.hot_comments,
            "rootComments": comment_obj.root_comments,
            "subCommentsMap": comment_obj.sub_comments,
            "save_unix": time.time()
        }
        return self._json_saver(comment_data, f"comment.json")

    def _save_danmaku(self, num: int = 1):
        assert num <= len(self.ac_obj.video_list)
        v_num = f"{self.ac_obj.ac_num}_{num}" if num > 1 else f"{self.ac_obj.ac_num}"
        self.ac_obj.set_video(num)
        danmaku_obj = self.ac_obj.danmaku()
        folder_path = self._setup_folder()
        danmaku_path = os.path.join(folder_path, 'danmaku')
        os.makedirs(danmaku_path, exist_ok=True)
        return self._json_saver(danmaku_obj.danmaku_data, f"{v_num}.json", danmaku_path)


class ArticleSaver(AcSaver):

    def __init__(self, acer, ac_obj):
        super().__init__(acer, ac_obj)

    def _save_content(self):
        self._save_member([self.ac_obj.article_data['user']['id']])
        folder_path = self._setup_folder()
        content_raw_saved = self._json_saver(self.ac_obj.article_data, f"content.json")
        article_template = self.templates.get_template('article.html')
        article_html = article_template.render(**self.ac_obj.article_data)
        html_obj = Bs(article_html, 'lxml')
        html_imgs_path = [self.folder_name, f"ac{self.ac_obj.ac_num}", 'imgs']
        self._renew_folder(os.path.join(folder_path, 'imgs'))
        for img in html_obj.select('img'):
            saved_path = self._save_images(img.attrs['src'], ex_dir=html_imgs_path)
            img.attrs['alt'] = img.attrs['src']
            img.attrs['src'] = f"./imgs/{os.path.basename(saved_path)}"
        html_path = os.path.join(self.dest_path, folder_path, f"main.html")
        with open(html_path, 'wb') as html_file:
            html_file.write(html_obj.prettify().encode())
        content_html_saved = os.path.isfile(html_path)
        return all([content_raw_saved, content_html_saved])

    pass


class MomentSaver(AcSaver):

    def _save_content(self):
        pass

    pass


class VideoSaver(AcSaver):

    def __init__(self, acer, ac_obj):
        super().__init__(acer, ac_obj)

    def _save_video(self, num: int = 1):
        assert num <= len(self.ac_obj.video_list)
        v_num = f"{self.ac_obj.ac_num}_{num}" if num > 1 else f"{self.ac_obj.ac_num}"
        self._save_member([self.ac_obj.video_data['user']['id']])
        folder_path = self._setup_folder()
        video_raw_saved = self._json_saver(self.ac_obj.video_data, f"video.json")
        acfun_url = f"{routes['video']}{v_num}"
        you_get_download(acfun_url, output_dir=folder_path, merge=True)
        video_saved = os.path.isfile(os.path.join(folder_path, f"{v_num}.mp4"))
        video_template = self.templates.get_template('video.html')
        video_html = video_template.render(v_num=v_num, **self.ac_obj.video_data)
        html_path = os.path.join(self.dest_path, folder_path, f"ac{v_num}.html")
        with open(html_path, 'wb') as html_file:
            html_file.write(video_html.encode())
        video_html_saved = os.path.isfile(html_path)
        video_danmaku_saved = self._save_danmaku(num)
        return all([video_raw_saved, video_html_saved, video_saved, video_danmaku_saved])

    pass


class BangumiSaver(AcSaver):

    def _save_season(self):
        pass

    def _save_episode(self):
        pass

    pass


class LiveSaver(AcSaver):
    pass
