# coding=utf-8
import os
import re
import time
import json
import arrow
import shutil
import zipfile
from uuid import uuid4
from urllib.parse import urlparse, urlencode
from .source import routes, apis
from .page.utils import downloader, danmaku2ass
from bs4 import BeautifulSoup as Bs
from alive_progress import alive_bar
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
    ubb_tag_basic = {
        r"\r\n": "<br>",
        "[b]": "<b>", "[/b]": "</b>",
        "[i]": "<i>", "[/i]": "</i>",
        "[u]": "<u>", "[/u]": "</u>",
        "[s]": "<s>", "[/s]": "</s>",
        "[/color]": r"</color>",
    }
    ubb_tag_rex = {
        "color": r"(\[color=(#[a-f0-9]{6})\])",
        "emot": r"(\[emot=acfun,(\S+?)\/])",
        "image": r"(\[img=图片\](http[^\s]*)\[/img\])",
        "at": r"(\[at uid=(\d+)\](@[^\[]+)\[/at\])",
        "resource": r"(\[resource id=(\d+) type=([1-5]) icon=[^\]]*\]([^\[]*)\[\/resource\])",
        "jump": r"(\[time duration=(\d+)\]([^\[]+)\[/time\])",
    }
    ubb_resource_url = {
        "1": routes['bangumi'],
        "2": routes['video'],
        "3": routes['article'],
        "4": routes['album'],
        "5": routes['up']
    }
    ubb_resource_icon = {
        "1": r'<img class=\"ubb-icon\" src=\"../../assets/img/icon_comment_video_pc.png\">',
        "2": r'<img class=\"ubb-icon\" src=\"../../assets/img/icon_comment_pc_vid_18_3.png\">',
        "3": r'<img class=\"ubb-icon\" src=\"../../assets/img/icon_popup_article_pc.png\">',
        "4": r'<img class=\"ubb-icon\" src=\"../../assets/img/icon_comment_heji_pc.png\">',
        "5": r'<img class=\"ubb-icon\" src=\"../../assets/img/icon_comment_human_pc.png\">',
    }

    def __init__(self, acer, ac_obj, dest_path=None):
        self.acer = acer
        self.ac_obj = ac_obj
        self.dest_path = dest_path or os.path.join(os.getcwd(), 'download')
        self.folder_name = self.obj2folder.get(self.ac_obj.__class__.__name__, "else")
        if not os.path.isdir(self.dest_path):
            os.makedirs(self.dest_path, exist_ok=True)
        self.cdns = self.acer.client.post(apis['cdn_domain'], headers={
            "referer": routes['index']}).json().get('domain')

    def _setup_folder(self):
        folder_path = os.path.join(self.dest_path, self.folder_name, f"ac{self.ac_obj.ac_num}")
        if self.folder_name in ["article", "moment", "video", "bangumi"]:
            os.makedirs(os.path.join(folder_path, 'img'), exist_ok=True)
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

    def _save_emot(self):
        emot_req = self.acer.client.post(apis['emot'])
        emot_data = emot_req.json()
        assert emot_data['result'] == 0
        emot_ex_dir = ['assets', 'emot']
        emot_dir = os.path.join(self.dest_path, *emot_ex_dir)
        os.makedirs(emot_dir, exist_ok=True)
        emot_json_saved = self._json_saver(emot_data, "emotion.json", emot_dir)
        for pack in emot_data['emotionPackageList']:
            if len(pack['downloadUrl']):
                fname = urlparse(pack['downloadUrl']).path.split('/')[-1]
                zip_path = os.path.join(emot_dir, f"{fname}.zip")
                if os.path.isfile(zip_path) is False:
                    self._download(pack['downloadUrl'], f"{fname}.zip", emot_ex_dir)
                if os.path.isfile(zip_path):
                    zip_file = zipfile.ZipFile(zip_path)
                    zip_file.extractall(os.path.dirname(zip_path))
            for em in pack['emotions']:
                for x, y in {'small': 'smallImageInfo', 'big': 'bigImageInfo'}.items():
                    em_src = em[y]['thumbnailImageCdnUrl']
                    em_ext = urlparse(em_src).path.split('/')[-1].split('.')[-1]
                    em_path = os.path.join(emot_dir, x, f"{em['id']}.{em_ext}")
                    if not os.path.isfile(em_path):
                        self._download(em_src, f"{em['id']}.{em_ext}", ['assets', 'emot', x])
        local_emot_list = os.listdir(os.path.join(emot_dir, 'big'))
        for n in range(1, 56):
            if f"{n}.gif" not in local_emot_list:
                src = f"https://cdnfile.aixifan.com/static/umeditor/emotion/images/ac/{n}.gif"
                self._download(src, f"{n}.gif", ['assets', 'emot', 'big'])
        local_emot_list = os.listdir(os.path.join(emot_dir, 'big'))
        emot_map = {em.split('.')[0]: f"../../assets/emot/big/{em}" for em in local_emot_list}
        emot_map_saved = self._json_saver(emot_map, "emotion_map.json", emot_dir)
        return all([emot_json_saved, emot_map_saved])

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

    def _save_member(self, ids: list, force: bool = False):
        done = list()
        member_dir = os.path.join(self.dest_path, 'member')
        saved = os.listdir(member_dir)
        with alive_bar(len(ids), length=30, disable=len(ids) < 5, title="save members",
                       force_tty=True, stats=False) as progress:
            for uid in ids:
                if all([f"{uid}.json" in saved, f"{uid}.js" in saved, f"{uid}_avatar" in saved]) is True \
                        and force is False:
                    progress()
                    continue
                user_req = self.acer.client.get(apis['userInfo'], params=dict(userId=uid))
                user_data = user_req.json()
                profile = user_data.get('profile')
                user_json = os.path.join(member_dir, f"{uid}.json")
                user_js = os.path.join(member_dir, f"{uid}.js")
                user_avatar = os.path.join(member_dir, f"{uid}_avatar")
                if all([os.path.isfile(user_json), os.path.isfile(user_js), os.path.isfile(user_avatar)]) is True \
                        and force is False:
                    progress()
                    continue
                with open(user_json, 'w') as uid_file:
                    json.dump(profile, uid_file, separators=(',', ':'))
                user_json_saved = os.path.isfile(user_json)
                user_json_string = open(os.path.join(user_json), 'rb').read().decode()
                with open(user_js, 'wb') as js_file:
                    user_js_string = f"let user_{uid}={user_json_string};"
                    js_file.write(user_js_string.encode())
                user_js_saved = os.path.isfile(user_js)
                avatar = urlparse(profile['headUrl'])
                avatar_path = self._save_images(f"{avatar.scheme}://{avatar.netloc}{avatar.path}", str(uid), ['member'])
                shutil.move(avatar_path, user_avatar)
                avatar_saved = os.path.isfile(user_avatar)
                if all([user_json_saved, user_js_saved, avatar_saved]):
                    done.append(uid)
                progress()
                time.sleep(0.1)
        return done

    def get_user(self, uid: str):
        self._save_member([uid], True)
        user_json_path = os.path.join(self.dest_path, 'member', f"{uid}.json")
        user_data = json.load(open(user_json_path, 'rb'))
        return user_data

    def _json_saver(self, data: dict, filename: str, dest_path=None):
        folder_path = self._setup_folder()
        json_path = os.path.join(self.dest_path, folder_path, filename)
        if dest_path is not None:
            json_path = os.path.join(dest_path, filename)
        json_string = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
        with open(json_path, 'wb') as json_file:
            json_file.write(json_string.encode())
        return os.path.isfile(json_path)

    def _save_comment(self):
        folder_path = self._setup_folder()
        local_comment_data, local_comment_floors = None, []
        comment_json_path = os.path.join(folder_path, f"ac{self.ac_obj.ac_num}.comment.json")
        if os.path.isfile(comment_json_path):
            local_comment_data = json.load(open(comment_json_path, 'rb'))
            local_comment_floors = [x['floor'] for x in local_comment_data['rootComments']]
        comment_obj = self.ac_obj.comment()
        comment_obj.get_all_comment()
        if local_comment_data is not None:
            comment_data = local_comment_data
            comment_data['hotComments'] = comment_obj.hot_comments
            comment_data['subCommentsMap'].update(comment_obj.sub_comments)
            comment_data['save_unix'] = time.time()
            comment_data['rootComments'].extend([c for c in comment_obj.root_comments
                                                 if c['floor'] not in local_comment_floors])
        else:
            comment_data = {
                "hotComments": comment_obj.hot_comments,
                "rootComments": comment_obj.root_comments,
                "subCommentsMap": comment_obj.sub_comments,
                "save_unix": time.time()
            }
        uids = list()
        for c in comment_data['rootComments']:
            if c['userId'] not in uids:
                uids.append(c['userId'])
        for _, i in comment_data['subCommentsMap'].items():
            for j in i['subComments']:
                if j['userId'] not in uids:
                    uids.append(j['userId'])
        self._save_member(uids)
        comment_saved = self._json_saver(comment_data, f"ac{self.ac_obj.ac_num}.comment.json")
        comment_js_path = self._tans_comment_uub2html()
        comment_js_saved = os.path.isfile(comment_js_path)
        return all([comment_saved, comment_js_saved])

    def _tans_comment_uub2html(self):
        folder_path = self._setup_folder()
        comment_json_path = os.path.join(folder_path, f"ac{self.ac_obj.ac_num}.comment.json")
        comment_js_path = os.path.join(folder_path, f"ac{self.ac_obj.ac_num}.comment.js")
        comment_json_string = open(comment_json_path, 'rb').read().decode()
        # 基础替换：换行,加粗,斜体,下划线,删除线,颜色结尾
        for ubb, tag in self.ubb_tag_basic.items():
            comment_json_string = comment_json_string.replace(ubb, tag)
        # 正则替换：颜色,表情,图片
        emot_map = json.load(open(os.path.join(self.dest_path, 'assets', 'emot', 'emotion_map.json'), 'r'))
        for n, rex_rule in self.ubb_tag_rex.items():
            for tag in re.compile(rex_rule).findall(comment_json_string):
                if n == 'color':
                    comment_json_string = comment_json_string.replace(
                        tag[0], f'<font color=\\"{tag[1]}\\">')
                elif n == 'emot':
                    if tag[1] in emot_map:
                        comment_json_string = comment_json_string.replace(
                            tag[0], f'<img class=\\"ubb-emotion\\" src=\\"{emot_map[tag[1]]}\\">')
                elif n == 'image':
                    img_path = self._save_images(tag[1], ex_dir=[self.folder_name, f"ac{self.ac_obj.ac_num}", 'img'])
                    img_name = os.path.basename(img_path)
                    comment_json_string = comment_json_string.replace(
                        tag[0], f'<img src=\\"img/{img_name}\\" alt=\\"{tag[1]}\\">')
                elif n == 'at':
                    comment_json_string = comment_json_string.replace(
                        tag[0], f'<a class=\\"ubb-name\\" target=\\"_blank\\" href=\\"https://www.acfun.cn/u/{tag[1]}\\">{tag[2]}</a>')
                elif n == 'jump':
                    comment_json_string = comment_json_string.replace(
                        tag[0], f'<a class=\\"quickJump\\" onclick=\\"quickJump({tag[1]})\\">{tag[2]}</a>')
                elif n == 'resource':
                    resource_a = '<a class=\\"ubb-ac\\" data-aid=\\"{ac_num}\\" href=\\"{href}\\" target=\\"_blank\\">{title}</a>'
                    comment_json_string = comment_json_string.replace(
                        tag[0], self.ubb_resource_icon[tag[2]]+resource_a.format(
                            ac_num=tag[1],
                            href=self.ubb_resource_url[tag[2]]+tag[1],
                            title=tag[3]
                        ))
        with open(comment_js_path, 'wb') as js_file:
            comment_js = f"let commentData={comment_json_string};"
            js_file.write(comment_js.encode())
        return comment_js_path

    def _save_danmaku(self, num: int = 1):
        assert num <= len(self.ac_obj.video_list)
        v_num = f"{self.ac_obj.ac_num}_{num}" if num > 1 else f"{self.ac_obj.ac_num}"
        folder_path = self._setup_folder()
        self.ac_obj.set_video(num)
        danmaku_obj = self.ac_obj.danmaku()
        danmaku_saved = self._json_saver(danmaku_obj.danmaku_data, f"ac{v_num}.danmaku.json")
        danmaku_json_string = open(os.path.join(folder_path, f"ac{v_num}.danmaku.json"), 'rb').read().decode()
        danmaku_js_path = os.path.join(folder_path, f"ac{v_num}.danmaku.js")
        with open(danmaku_js_path, 'wb') as js_file:
            danmaku_js = f"let danmakuData={danmaku_json_string};"
            js_file.write(danmaku_js.encode())
        danmaku_js_saved = os.path.isfile(danmaku_js_path)
        danmaku_ass_path = self._danmaku2ass(num)
        danmaku_ass_saved = os.path.isfile(danmaku_ass_path)
        danmaku_ass_js_path = os.path.join(folder_path, f"ac{v_num}.ass.js")
        danmaku_ass_js_saved = os.path.isfile(danmaku_ass_js_path)
        return all([danmaku_saved, danmaku_js_saved, danmaku_ass_saved, danmaku_ass_js_saved])

    def _danmaku2ass(self, num: int = 1):
        assert num <= len(self.ac_obj.video_list)
        v_num = f"{self.ac_obj.ac_num}_{num}" if num > 1 else f"{self.ac_obj.ac_num}"
        folder_path = self._setup_folder()
        self.ac_obj.set_video(num)
        return danmaku2ass(self.acer.client, folder_path, f"ac{v_num}")

    def _save_qrcode(self, url: [str, None] = None, filename: str = "share_qrcode.png"):
        size = 200
        param = {
            "content": url or self.ac_obj.share_url,
            "contentType": "URL",
            "toShortUrl": False,
            "width": size,
            "height": size
        }
        qr_url = f"{apis['qrcode']}?{urlencode(param)}"
        return self._save_images(qr_url, filename, ex_dir=[self.folder_name, f"ac{self.ac_obj.ac_num}"])


class ArticleSaver(AcSaver):

    def __init__(self, acer, ac_obj):
        super().__init__(acer, ac_obj)

    def _save_content(self):
        self._save_member([self.ac_obj.article_data['user']['id']])
        folder_path = self._setup_folder()
        v_num = f"{self.ac_obj.ac_num}"
        up_data = self.get_user(self.ac_obj.article_data['user']['id'])
        content_raw_saved = self._json_saver(self.ac_obj.article_data, f"ac{v_num}.json")
        content_json_string = open(os.path.join(folder_path, f"ac{v_num}.json"), 'rb').read().decode()
        content_js_path = os.path.join(folder_path, f"ac{v_num}.js")
        with open(content_js_path, 'wb') as js_file:
            content_js = f"let contentData={content_json_string};"
            js_file.write(content_js.encode())
        content_js_saved = os.path.isfile(content_js_path)
        article_template = self.templates.get_template('article.html')
        article_html = article_template.render(
            up_reg_date=arrow.get(up_data['registerTime']).format("YYYY-MM-DD HH:mm:ss"),
            cache_date=arrow.now().format("YYYY-MM-DD HH:mm:ss"),
            v_num=v_num, up_data=up_data, **self.ac_obj.article_data)
        html_obj = Bs(article_html, 'lxml')
        html_img_path = [self.folder_name, f"ac{self.ac_obj.ac_num}", 'img']
        self._renew_folder(os.path.join(folder_path, 'img'))
        for img in html_obj.select('img'):
            if img.attrs['src'].startswith('http') or img.attrs['src'].startswith('//'):
                saved_path = self._save_images(img.attrs['src'], ex_dir=html_img_path)
                img.attrs['alt'] = img.attrs['src']
                img.attrs['src'] = f"./img/{os.path.basename(saved_path)}"
        comment_saved = self._save_comment()
        html_path = os.path.join(self.dest_path, folder_path, f'ac{v_num}.html')
        with open(html_path, 'wb') as html_file:
            html_file.write(html_obj.prettify().encode())
        content_html_saved = os.path.isfile(html_path)
        cover_path = self._save_images(self.ac_obj.article_data['coverUrl'], 'cover',
                                       [self.folder_name, f"ac{self.ac_obj.ac_num}"])
        cover_saved = os.path.isfile(cover_path)
        share_qrcode_path = self._save_qrcode()
        share_qrcode_saved = os.path.isfile(share_qrcode_path)
        return all([
            content_raw_saved,
            content_js_saved,
            comment_saved,
            cover_saved,
            share_qrcode_saved,
            content_html_saved
        ])

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
        up_data = self.get_user(self.ac_obj.video_data['user']['id'])
        folder_path = self._setup_folder()
        video_raw_saved = self._json_saver(self.ac_obj.video_data, f"ac{v_num}.json")
        video_json_string = open(os.path.join(folder_path, f"ac{v_num}.json"), 'rb').read().decode()
        video_js_path = os.path.join(folder_path, f"ac{v_num}.js")
        with open(video_js_path, 'wb') as js_file:
            content_js = f"let videoData={video_json_string};"
            js_file.write(content_js.encode())
        video_js_saved = os.path.isfile(video_js_path)
        acfun_url = f"{routes['video']}{v_num}"
        you_get_download(acfun_url, output_dir=folder_path, merge=True)
        video_saved = os.path.isfile(os.path.join(folder_path, f"{v_num}.mp4"))
        video_template = self.templates.get_template('video.html')
        video_html = video_template.render(
            up_reg_date=arrow.get(up_data['registerTime']).format("YYYY-MM-DD HH:mm:ss"),
            cache_date=arrow.now().format("YYYY-MM-DD HH:mm:ss"),
            v_num=v_num, up_data=up_data, **self.ac_obj.video_data)
        cover_path = self._save_images(self.ac_obj.video_data['coverUrl'], 'cover',
                                       [self.folder_name, f"ac{self.ac_obj.ac_num}"])
        cover_saved = os.path.isfile(cover_path)
        share_qrcode_path = self._save_qrcode()
        share_qrcode_saved = os.path.isfile(share_qrcode_path)
        mobile_qrcode_path = self._save_qrcode(self.ac_obj.mobile_url, "mobile_qrcode.png")
        mobile_qrcode_saved = os.path.isfile(mobile_qrcode_path)
        comment_saved = self._save_comment()
        html_path = os.path.join(self.dest_path, folder_path, f"ac{v_num}.html")
        with open(html_path, 'wb') as html_file:
            html_file.write(video_html.encode())
        video_html_saved = os.path.isfile(html_path)
        video_danmaku_saved = self._save_danmaku(num)
        return all([
            video_raw_saved,
            video_js_saved,
            video_saved,
            cover_saved,
            share_qrcode_saved,
            mobile_qrcode_saved,
            video_danmaku_saved,
            comment_saved,
            video_html_saved
        ])

    pass


class BangumiSaver(AcSaver):

    def _save_season(self):
        pass

    def _save_episode(self):
        pass

    pass


class LiveSaver(AcSaver):
    pass
