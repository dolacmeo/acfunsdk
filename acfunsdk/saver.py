# coding=utf-8
import math
import os
import re
import time
import json
import math
import shutil
import zipfile
from uuid import uuid4
from urllib.parse import urlparse, urlencode
from .source import routes, apis
from .page.utils import downloader, danmaku2ass, acfun_video_downloader
from bs4 import BeautifulSoup as Bs
from rich.progress import Progress
from jinja2 import PackageLoader, Environment

__author__ = 'dolacmeo'


def unix2datestr(t: (int, float, None) = None, f: str = "%Y-%m-%d %H:%M:%S"):
    if t is None:
        return time.strftime(f, time.localtime(time.time()))
    t = int(t)
    n = int(math.log10(t))
    if n > 10:
        t = t // math.pow(10, n - 10)
    elif n < 10:
        t = t * math.pow(10, 10 - n)
    return time.strftime(f, time.localtime(t))


class AcSaver:
    templates = Environment(loader=PackageLoader('acfunsdk', 'templates'))
    templates.filters['unix2datestr'] = unix2datestr
    templates.filters['math_ceil'] = math.ceil
    folder_names = ['article', 'video', 'bangumi', 'live', 'moment']
    emot_alias = ['default', 'ac', 'ac2', 'ac3', 'dog', 'tsj', 'brd', 'ais', 'td', 'zuohe', 'blizzard']
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
        "[/color]": r"</color>"
    }
    ubb_tag_rex = {
        "color": r"(\[color=(#[a-f0-9]{6})\])",
        "size": r"(\[size=(\d+px)\]([^\[]+)\[/size\])",
        "emot": r"(\[emot=acfun,(\S+?)\/])",
        "emot_old": r"(\[emot=([a-z0-9]+),(\S+?)\/])",
        "image": r"(\[img=\\u56fe\\u7247\]([^\[]*)\[\/img\])",
        "at": r"(\[at uid=(\d+)\](@[^\[]+)\[/at\])",
        "at_old": r"(\[at\]([^\[]+)\[/at\])",
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
        self.folder_name = "else" if ac_obj is None else self.obj2folder.get(self.ac_obj.__class__.__name__, "else")
        if not os.path.isdir(self.dest_path):
            os.makedirs(self.dest_path, exist_ok=True)
        self.cdns = self.acer.client.post(apis['cdn_domain'], headers={
            "referer": routes['index']}).json().get('domain')
        self._check_folders()
        # self._check_assets()

    def _check_folders(self):
        checks = list()
        for x in self.folder_names:
            x_path = os.path.join(self.dest_path, x)
            os.makedirs(x_path, exist_ok=True)
            checks.append(os.path.isdir(x_path))
        os.makedirs(os.path.join(self.dest_path, 'member'), exist_ok=True)
        index_html = self.templates.get_template('index.html').render()
        index_html_path = os.path.join(self.dest_path, 'index.html')
        if os.path.isfile(index_html_path) is False:
            self._check_assets()
        with open(index_html_path, 'wb') as i:
            i.write(index_html.encode())
        return all(checks)

    def _check_assets(self):
        if os.path.isdir(os.path.join(self.dest_path, 'assets')) is False:
            return False
        checks = list()
        checks.append(os.path.isfile(os.path.join(self.dest_path, 'assets', 'favicon.ico')))
        for n in ['css', 'js', 'img', 'font', 'emot']:
            checks.append(os.path.isdir(os.path.join(self.dest_path, 'assets', n)))
        return all(checks)

    def download_assets_from_github(self):
        assert_zip_path = os.path.join(self.dest_path, 'assets.zip')
        assert_zip_saved = os.path.isfile(assert_zip_path)
        if assert_zip_saved is False:
            assets_url = r"https://archive.fastgit.org/dolaCmeo/acfunSDK/archive/refs/heads/assets.zip"
            assert_download = self._download(assets_url, display=True)
            if assert_download is None:
                return False
        zip_file = zipfile.ZipFile(assert_zip_path)
        zip_file.extractall(self.dest_path)
        assert_zip_folder = os.path.join(self.dest_path, 'acfunSDK-assets', 'assets')
        assert_folder = os.path.join(self.dest_path, 'assets')
        shutil.move(assert_zip_folder, assert_folder)
        shutil.rmtree(os.path.join(self.dest_path, 'acfunSDK-assets'), ignore_errors=True)
        assert_folder_ok = os.path.isdir(assert_folder)
        if assert_folder_ok is True:
            emot_map_path = os.path.join(self.dest_path, 'assets', 'emot', 'emotion_map.json')
            if os.path.isfile(emot_map_path) is False:
                self.save_emot()
        return assert_folder_ok

    def folder_list_update(self):
        jsFiles = []
        for fn in self.folder_names:
            fpath = os.path.join(self.dest_path, fn)
            f_all = os.listdir(fpath)
            f_all = [i for i in f_all if os.path.isdir(os.path.join(fpath, i))]
            f_all_string = json.dumps(f_all, separators=(',', ':'))
            nums_js = f"let {fn}Nums={f_all_string};"
            js_path = os.path.join(fpath, 'nums.js')
            with open(os.path.join(fpath, 'nums.js'), 'wb') as js:
                js.write(nums_js.encode())
            jsFiles.append(os.path.isfile(js_path))
        return all(jsFiles)

    def record_last(self):
        ac_num = f"ac{self.ac_obj.ac_num}"
        if "_" in ac_num:
            ac_num = ac_num.split('_')[0]

        last_data = []
        last_path = os.path.join(self.dest_path, self.folder_name, 'leatest.js')
        if os.path.isfile(last_path):
            sn = len(f"{self.folder_name}Last=")
            last_text = open(last_path, 'r').read()
            last_data = json.loads(last_text.strip()[sn:-1])
        if ac_num not in last_data:
            last_data.append(ac_num)
        last_string = json.dumps(last_data, separators=(',', ':'))
        last_js = f"{self.folder_name}Last={last_string};"
        with open(last_path, 'wb') as js:
            js.write(last_js.encode())

        recent_data = []
        recent_path = os.path.join(self.dest_path, 'assets', 'data', 'recent.js')
        if os.path.isfile(recent_path):
            recent_text = open(recent_path, 'r').read()
            recent_data = json.loads(recent_text.strip()[12:-1])
        if [self.folder_name, ac_num] not in recent_data:
            recent_data.append([self.folder_name, ac_num])
        recent_string = json.dumps(recent_data, separators=(',', ':'))
        recent_js = f"AcCacheList={recent_string};"
        with open(recent_path, 'wb') as js:
            js.write(recent_js.encode())

        return all([os.path.isfile(last_path), os.path.isfile(recent_path)])

    def _setup_folder(self):
        folder_path = os.path.join(self.dest_path, self.folder_name, f"ac{self.ac_obj.ac_num}")
        os.makedirs(os.path.join(folder_path, 'data'), exist_ok=True)
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

    def _download(self, src_url: str, fname: [str, None] = None, ex_dir: [list, None] = None, display: bool = False):
        save_path = self.dest_path if ex_dir is None else os.path.join(self.dest_path, *ex_dir)
        return downloader(self.acer.client, src_url, fname, save_path, display)

    def save_emot(self):
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
        emot_map_path = os.path.join(emot_dir, "emotion_map.json")
        emot_map = {"saved": {}, "lost": []}
        if os.path.isfile(emot_map_path) is True:
            emot_map = json.load(open(emot_map_path, 'rb'))
        else:
            for emot_name in os.listdir(emot_dir):
                this_path = os.path.join(emot_dir, emot_name)
                if os.path.isdir(this_path) is False or emot_name in ['small']:
                    continue
                files = os.listdir(this_path)
                emot_map['saved'].update({
                    f"acfun,{x.split('.')[0]}" if emot_name == 'big' else f"{emot_name},{x.split('.')[0]}":
                        f"../../assets/emot/{emot_name}/{x}"
                    for x in files
                })
        for alias in self.emot_alias:
            alias_emot_path = os.path.join(emot_dir, alias)
            os.makedirs(alias_emot_path, exist_ok=True)
            alias_emot_list = os.listdir(alias_emot_path)
            for n in range(1, 60):
                if n < 10:
                    map_name0 = f"{alias},{n}"
                    if f"{n}.gif" in alias_emot_list:
                        emot_map['saved'].update({f"{map_name0}":  f"../../assets/emot/{alias}/{n}.gif"})
                        continue
                    elif map_name0 in emot_map['lost']:
                        continue
                    src = f"https://cdnfile.aixifan.com/static/umeditor/emotion/images/{alias}/{n}.gif"
                    name0_save = self._download(src, f"{n}.gif", ['assets', 'emot', alias])
                    if name0_save is None:
                        emot_map['lost'].append(map_name0)
                    elif os.path.isfile(name0_save):
                        emot_map['saved'].update({f"{map_name0}": f"../../assets/emot/{alias}/{n}.gif"})
                    else:
                        print("EMOT UNKNOWN:", map_name0)
                map_name1 = f"{alias},{n:0>2}"
                if f"{n:0>2}.gif" in alias_emot_list:
                    emot_map['saved'].update({f"{map_name1}":  f"../../assets/emot/{alias}/{n:0>2}.gif"})
                    continue
                elif map_name1 in emot_map['lost']:
                    continue
                src = f"https://cdnfile.aixifan.com/static/umeditor/emotion/images/{alias}/{n:0>2}.gif"
                name1_save = self._download(src, f"{n:0>2}.gif", ['assets', 'emot', alias])
                if name1_save is None:
                    emot_map['lost'].append(map_name1)
                elif os.path.isfile(name1_save):
                    emot_map['saved'].update({f"{map_name1}": f"../../assets/emot/{alias}/{n:0>2}.gif"})
                else:
                    print("EMOT UNKNOWN:", map_name1)
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
        return self._download(src_url, fname, ex_dir, display=False)

    def _save_member(self, ids: list, force: bool = False):
        if len(ids) == 0:
            return []
        done = list()
        member_dir = os.path.join(self.dest_path, 'member')
        saved = os.listdir(member_dir)
        ids = sorted(list(set(ids)))
        ids_with_ext = [f"{i}.json" for i in ids]
        ids = list(set(ids_with_ext).difference([x for x in saved if x.endswith('.json')]))
        ids = [y.split('.')[0] for y in ids]
        with Progress() as pp:
            get_member = pp.add_task("save members", total=len(ids))
            for uid in ids:
                if all([f"{uid}.json" in saved, f"{uid}.js" in saved, f"{uid}_avatar" in saved]) is True \
                        and force is False:
                    pp.update(get_member, advance=1)
                    done.append(uid)
                    continue
                user_req = self.acer.client.get(apis['userInfo'], params=dict(userId=uid))
                user_data = user_req.json()
                profile = user_data.get('profile')
                user_json = os.path.join(member_dir, f"{uid}.json")
                user_js = os.path.join(member_dir, f"{uid}.js")
                user_avatar = os.path.join(member_dir, f"{uid}_avatar")
                if all([os.path.isfile(user_json), os.path.isfile(user_js), os.path.isfile(user_avatar)]) is True \
                        and force is False:
                    pp.update(get_member, advance=1)
                    done.append(uid)
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
                if avatar.path.endswith('defaultAvatar.jpg'):
                    avatar_saved = True
                else:
                    avatar_path = self._save_images(f"{avatar.scheme}://{avatar.netloc}{avatar.path}", str(uid), ['member'])
                    avatar_saved = False if avatar_path is None else os.path.isfile(avatar_path)
                    if avatar_saved:
                        shutil.move(avatar_path, user_avatar)
                if all([user_json_saved, user_js_saved, avatar_saved]):
                    done.append(uid)
                pp.update(get_member, advance=1)
                time.sleep(0.1)
            pp.update(get_member, completed=len(ids))
            pp.stop()
        return done

    def get_user(self, uid: str):
        self._save_member([uid], True)
        user_json_path = os.path.join(self.dest_path, 'member', f"{uid}.json")
        user_data = json.load(open(user_json_path, 'rb'))
        return user_data

    def _json_saver(self, data: dict, filename: str, dest_path=None):
        folder_path = self._setup_folder()
        json_path = os.path.join(folder_path, 'data', filename)
        if dest_path is not None:
            json_path = os.path.join(dest_path, filename)
        json_string = json.dumps(data, separators=(',', ':'))
        with open(json_path, 'wb') as json_file:
            json_file.write(json_string.encode())
        result = os.path.isfile(json_path)
        print("SAVED:", result, json_path)
        return result

    def _save_comment(self, update: bool = False):
        folder_path = self._setup_folder()
        local_comment_data, local_comment_floors = None, []
        comment_json_path = os.path.join(folder_path, 'data', f"ac{self.ac_obj.ac_num}.comment.json")
        comment_json_path_saved = os.path.isfile(comment_json_path)
        if comment_json_path_saved:
            print("loading comment data.json")
            local_comment_data = json.load(open(comment_json_path, 'rb'))
            local_comment_floors = [x['floor'] for x in local_comment_data['rootComments']]
        if update is True or comment_json_path_saved is False:
            comment_obj = self.ac_obj.comment()
            comment_obj.get_all_comment()
            if local_comment_data is not None:
                comment_data = local_comment_data
                comment_data['hotComments'] = comment_obj.hot_comments
                comment_data['rootComments'].extend(
                    [c for c in comment_obj.root_comments if c['floor'] not in local_comment_floors])
                comment_data['subCommentsMap'].update(comment_obj.sub_comments)
                comment_data['save_unix'] = time.time()
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
            print("SAVED:", comment_saved, comment_json_path)
        else:
            comment_saved = True
        comment_js_saved = self._tans_comment_uub2html()
        return all([comment_saved, comment_js_saved])

    def _tans_comment_uub2html(self):
        print("loading comment data json")
        folder_path = self._setup_folder()
        comment_json_path = os.path.join(folder_path, 'data', f"ac{self.ac_obj.ac_num}.comment.json")
        comment_json_temp = os.path.join(folder_path, 'data', f"ac{self.ac_obj.ac_num}.comment.temp")
        temp_ok = os.path.isfile(comment_json_temp)
        if temp_ok:
            print('loading temp')
            comment_json_string = open(comment_json_temp, 'r').read()
        else:
            comment_json_string = open(comment_json_path, 'r').read()
            print('process comment ubb tags')
            # 基础替换：换行,加粗,斜体,下划线,删除线,颜色结尾
            for ubb, tag in self.ubb_tag_basic.items():
                comment_json_string = comment_json_string.replace(ubb, tag)
            # 正则替换：颜色,表情,图片
            emot_map_path = os.path.join(self.dest_path, 'assets', 'emot', 'emotion_map.json')
            if os.path.isfile(emot_map_path) is False:
                self.save_emot()
            emot_map = json.load(open(emot_map_path, 'r'))
            for n, rex_rule in self.ubb_tag_rex.items():
                for tag in re.compile(rex_rule).findall(comment_json_string):
                    if n == 'color':
                        comment_json_string = comment_json_string.replace(
                            tag[0], f'<font color=\\"{tag[1]}\\">')
                    elif n == 'size':
                        comment_json_string = comment_json_string.replace(
                            tag[0], f'<span style=\\"font-size:{tag[1]}\\">{tag[2]}</span>')
                    elif n == 'emot':
                        if tag[1] in emot_map:
                            comment_json_string = comment_json_string.replace(
                                tag[0], f'<img class=\\"ubb-emotion\\" src=\\"{emot_map[tag[1]]}\\">')
                    elif n == 'emot_old':
                        alias = ",".join(tag[1:])
                        if alias in emot_map['saved']:
                            comment_json_string = comment_json_string.replace(
                                tag[0], f'<img class=\\"ubb-emotion\\" src=\\"{emot_map["saved"][alias]}\\">')
                        elif alias in emot_map['lost']:
                            pass
                        else:
                            print("??? emot:", tag)
                    elif n == 'image':
                        img_path = self._save_images(tag[1], ex_dir=[self.folder_name, f"ac{self.ac_obj.ac_num}", 'img'])
                        if img_path is None:
                            print(f"IMG ERROR: {tag[1]}")
                            comment_json_string = comment_json_string.replace(
                                tag[0], f'<img class=\\"lazy\\" data-src=\\"../../assets/img/404img.png\\" alt=\\"{tag[1]}\\">')
                        else:
                            img_name = os.path.basename(img_path)
                            comment_json_string = comment_json_string.replace(
                                tag[0], f'<img class=\\"lazy\\" data-src=\\"img/{img_name}\\" alt=\\"{tag[1]}\\">')
                    elif n == 'at':
                        comment_json_string = comment_json_string.replace(
                            tag[0], f'<a class=\\"ubb-name\\" target=\\"_blank\\" href=\\"https://www.acfun.cn/u/{tag[1]}\\">{tag[2]}</a>')
                    elif n == 'at_old':
                        comment_json_string = comment_json_string.replace(
                            tag[0], f'<a class=\\"ubb-name\\">@{tag[1]}</a>')
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
            # for tag in re.compile(r"(\[([^\]]+)\])").findall(comment_json_string):
            #     print(tag)
            print('SAVE TEMP')
            with open(comment_json_temp, 'w') as t:
                t.write(comment_json_string)
        print('split comment data')
        comment_data = json.loads(comment_json_string)
        total_comment = len(comment_data['rootComments'])
        # 评论分块存储，每块100条；跟楼按每页划分。
        # 区块正向划分，预留已删除位置；区块顺序列表倒置；热评在最后。
        total_block = math.ceil(total_comment / 100)
        blocks = {}
        count = 0
        for X in comment_data['rootComments']:
            count += 1
            z = str(math.floor(X['floor'] / 100))
            if z not in blocks:
                blocks[z] = {
                    "hotComments": [],
                    "rootComments": [],
                    "subCommentsMap": {},
                    "save_unix": time.time(),
                    "totalComment": total_comment
                }
            blocks[z]['rootComments'].append(X)
            cid = str(X['commentId'])
            if cid in comment_data['subCommentsMap']:
                blocks[z]['subCommentsMap'][cid] = comment_data['subCommentsMap'][cid]
        totals = 0
        for v in blocks.values():
            totals += len(v["rootComments"])
        blocks = [j for i, j in sorted(blocks.items(), reverse=True)]
        blocks[0]["hotComments"] = comment_data["hotComments"]
        for Y in blocks[0]["hotComments"]:
            cid = str(Y['commentId'])
            if cid not in blocks[0]['subCommentsMap'] and cid in comment_data['subCommentsMap']:
                blocks[0]['subCommentsMap'][cid] = comment_data['subCommentsMap'][cid]
        for i in range(len(blocks)):
            B = blocks[i]
            B.update({'page': i + 1, 'total': len(blocks)})
            B['rootComments'] = sorted(B['rootComments'], key=lambda x: x['floor'], reverse=True)
            comment_block_js_path = os.path.join(folder_path, 'data', f"ac{self.ac_obj.ac_num}.comment.{i+1}.js")
            comment_block_js_string = json.dumps(B, separators=(',', ':'))
            with open(comment_block_js_path, 'wb') as js_file:
                comment_js = f"commentData[{i+1}]={comment_block_js_string};"
                js_file.write(comment_js.encode())
            print("SAVED:", os.path.isfile(comment_block_js_path), comment_block_js_path)
        if temp_ok:
            os.remove(comment_json_temp)
        return os.path.isfile(comment_json_path)

    def _save_danmaku(self, num: int = 1):
        assert num <= len(self.ac_obj.video_list)
        v_num = f"{self.ac_obj.ac_num}_{num}" if num > 1 else f"{self.ac_obj.ac_num}"
        folder_path = self._setup_folder()
        self.ac_obj.set_video(num)
        danmaku_obj = self.ac_obj.danmaku()
        danmaku_saved = self._json_saver(danmaku_obj.danmaku_data, f"ac{v_num}.danmaku.json")
        danmaku_json_string = open(os.path.join(folder_path, 'data', f"ac{v_num}.danmaku.json"), 'rb').read().decode()
        danmaku_js_path = os.path.join(folder_path, 'data', f"ac{v_num}.danmaku.js")
        with open(danmaku_js_path, 'wb') as js_file:
            danmaku_js = f"let ac{v_num}_danmaku={danmaku_json_string};"
            js_file.write(danmaku_js.encode())
        danmaku_js_saved = os.path.isfile(danmaku_js_path)
        print("SAVED:", danmaku_js_saved, danmaku_js_path)
        danmaku_ass_path = self._danmaku2ass(num)
        if danmaku_ass_path is None:
            danmaku_ass_saved, danmaku_ass_js_saved = True, True
        else:
            danmaku_ass_saved = os.path.isfile(danmaku_ass_path)
            danmaku_ass_js_path = os.path.join(folder_path, 'data', f"ac{v_num}.ass.js")
            danmaku_ass_js_saved = os.path.isfile(danmaku_ass_js_path)
            print("SAVED:", danmaku_ass_js_saved, danmaku_ass_js_path)
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
        return self._save_images(qr_url, filename, ex_dir=[self.folder_name, f"ac{self.ac_obj.ac_num}", 'data'])


class ArticleSaver(AcSaver):

    def __init__(self, acer, ac_obj, dest_path=None):
        super().__init__(acer, ac_obj, dest_path)
        self.folder_path = self._setup_folder()
        self.v_num = f"{self.ac_obj.ac_num}"

    def _save_base_data(self):
        content_raw_saved = self._json_saver(self.ac_obj.article_data, f"ac{self.v_num}.json")
        content_json_string = open(os.path.join(self.folder_path, 'data', f"ac{self.v_num}.json"), 'rb').read().decode()
        content_js_path = os.path.join(self.folder_path, 'data', f"ac{self.v_num}.js")
        with open(content_js_path, 'wb') as js_file:
            content_js = f"articles['ac{self.v_num}']={content_json_string};"
            js_file.write(content_js.encode())
        content_js_saved = os.path.isfile(content_js_path)
        return all([content_raw_saved, content_js_saved])

    def _save_page(self):
        cover_path = self._save_images(self.ac_obj.article_data['coverUrl'], 'cover',
                                       [self.folder_name, f"ac{self.ac_obj.ac_num}"])
        cover_saved = os.path.isfile(cover_path)
        shutil.copy(cover_path, os.path.join(self.dest_path, self.folder_path, f"cover._"))
        share_qrcode_path = self._save_qrcode()
        share_qrcode_saved = os.path.isfile(share_qrcode_path)
        up_data = self.get_user(self.ac_obj.article_data['user']['id'])
        article_template = self.templates.get_template('article.html')
        article_html = article_template.render(
            cache_date=unix2datestr(),
            up_reg_date=unix2datestr(up_data['registerTime']),
            v_num=self.v_num, up_data=up_data, RAW=self.ac_obj.article_data)
        html_obj = Bs(article_html, 'lxml')
        html_img_path = [self.folder_name, f"ac{self.ac_obj.ac_num}", 'img']
        self._renew_folder(os.path.join(self.folder_path, 'img'))
        for img in html_obj.select('.article-content img'):
            if img.attrs['src'].startswith('http') or img.attrs['src'].startswith('//'):
                saved_path = self._save_images(img.attrs['src'], ex_dir=html_img_path)
                img.attrs['alt'] = img.attrs['src']
                img.attrs['class'] = "lazy"
                img.attrs['src'] = "../../assets/img/logo-gray.png"
                img.attrs['data-src'] = f"./img/{os.path.basename(saved_path)}"
        html_path = os.path.join(self.dest_path, self.folder_path, f'ac{self.v_num}.html')
        with open(html_path, 'wb') as html_file:
            html_file.write(html_obj.prettify().encode())
        content_html_saved = os.path.isfile(html_path)
        return all([cover_saved, share_qrcode_saved, content_html_saved])

    def save_all(self):
        assert os.path.isfile(os.path.join(self.dest_path, 'assets', 'emot', 'emotion_map.json')) is True
        # 保存文章数据
        data_saved = self._save_base_data()
        # 保存文章封面、二维码、页面与图片
        page_saved = self._save_page()
        # 保存作者信息
        up_saved = self._save_member([self.ac_obj.article_data['user']['id']])
        # 保存评论
        comment_saved = self._save_comment()
        done = all([
            data_saved,
            page_saved,
            comment_saved
        ])
        if done:
            self.record_last()
            self.folder_list_update()
        print(self.folder_path)
        return done

    pass


class MomentSaver(AcSaver):

    def _save_content(self):
        pass

    pass


class VideoSaver(AcSaver):

    def __init__(self, acer, ac_obj, dest_path=None):
        super().__init__(acer, ac_obj, dest_path)
        self.folder_path = self._setup_folder()

    def _save_base_data(self, num: int = 1):
        v_num = f"{self.ac_obj.ac_num}_{num}" if num > 1 else f"{self.ac_obj.ac_num}"
        video_raw_saved = self._json_saver(self.ac_obj.video_data, f"ac{v_num}.json")
        video_json_string = open(os.path.join(self.folder_path, 'data', f"ac{v_num}.json"), 'rb').read().decode()
        video_js_path = os.path.join(self.folder_path, 'data', f"ac{v_num}.js")
        with open(video_js_path, 'wb') as js_file:
            content_js = f"videos['ac{v_num}']={video_json_string};"
            js_file.write(content_js.encode())
        video_js_saved = os.path.isfile(video_js_path)
        print("SAVED:", video_js_saved, video_js_path)
        return all([video_raw_saved, video_js_saved])

    def _save_page(self, num: int = 1):
        v_num = f"{self.ac_obj.ac_num}_{num}" if num > 1 else f"{self.ac_obj.ac_num}"
        cover_path = self._save_images(
            self.ac_obj.video_data['coverUrl'], 'cover', [self.folder_name, f"ac{self.ac_obj.ac_num}"])
        cover_saved = False if cover_path is None else os.path.isfile(cover_path)
        cover__path = os.path.join(self.dest_path, self.folder_path, f"cover._")
        if cover_saved:
            shutil.copy(cover_path, cover__path)
        else:
            ac404 = os.path.join(self.dest_path, 'assets', 'img', 'default_cover.png')
            shutil.copy(ac404, os.path.join(self.dest_path, self.folder_path, f"cover._"))
            cover_saved = os.path.isfile(cover__path)
        print("SAVED:", cover_saved, cover__path)
        if num == 1:
            share_qrcode_path = self._save_qrcode()
            share_qrcode_saved = os.path.isfile(share_qrcode_path)
            mobile_qrcode_path = self._save_qrcode(self.ac_obj.mobile_url, "mobile_qrcode.png")
            mobile_qrcode_saved = os.path.isfile(mobile_qrcode_path)
        else:
            cover_saved, share_qrcode_saved, mobile_qrcode_saved = True, True, True
        up_data = self.get_user(self.ac_obj.video_data['user']['id'])
        video_template = self.templates.get_template('video.html')
        video_html = video_template.render(
            cache_date=unix2datestr(),
            up_reg_date=unix2datestr(up_data['registerTime']), partNum=num,
            v_num=v_num, up_data=up_data, RAW=self.ac_obj.video_data)
        html_path = os.path.join(self.dest_path, self.folder_path, f"ac{v_num}.html")
        with open(html_path, 'wb') as html_file:
            html_file.write(video_html.encode(errors='ignore'))
        video_html_saved = os.path.isfile(html_path)
        print("SAVED:", video_html_saved, html_path)
        return all([cover_saved, share_qrcode_saved, mobile_qrcode_saved, video_html_saved])

    def save_video(self, num: int = 1):
        assert 0 < num <= len(self.ac_obj.video_list)
        v_num = f"{self.ac_obj.ac_num}_{num}" if num > 1 else f"{self.ac_obj.ac_num}"
        # 保存视频数据
        data_saved = self._save_base_data(num)
        # 保存视频封面、二维码、页面
        page_saved = self._save_page(num)
        # 保存作者信息
        uids = [self.ac_obj.video_data['user']['id']]
        staff = self.ac_obj.video_data.get('staffInfos', [])
        if len(staff):
            uids.extend([user['href'] for user in staff])
        up_saved = self._save_member(uids)
        # 保存视频弹幕
        danmaku_saved = self._save_danmaku(num)
        # 保存视频文件
        acfun_url = f"{routes['video']}{v_num}"
        video_path = os.path.join(self.folder_path, f"ac{v_num}.mp4")
        video_saved = os.path.isfile(video_path)
        if video_saved is False:
            video_saved_path = acfun_video_downloader(self.acer.client, self.ac_obj.video_data, self.folder_path, 0)
            if video_saved_path is not False:
                shutil.move(video_saved_path, video_path)
        print("SAVED:", video_saved, video_path)
        # 保存评论
        comment_saved = self._save_comment() if num == 1 else True
        done = all([
            data_saved,
            page_saved,
            danmaku_saved,
            video_saved,
            comment_saved
        ])
        if done:
            self.record_last()
            self.folder_list_update()
        print(self.folder_path)
        return done

    def save_all(self):
        result = []
        for i in range(len(self.ac_obj.video_list)):
            result.append(self.save_video(i + 1))
        return all(result)

    pass


class BangumiSaver(AcSaver):

    def _save_season(self):
        pass

    def _save_episode(self):
        pass

    pass


class LiveSaver(AcSaver):
    pass
