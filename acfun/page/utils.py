# coding=utf-8
import re
import os
import time
import math
import json
import httpx
import random
import base64
import shutil
import cssutils
import filetype
import subprocess
from uuid import uuid4
from urllib import parse
from urllib.parse import urlparse
from bs4 import BeautifulSoup as Bs
from bs4.element import Tag
from datetime import timedelta
from alive_progress import alive_bar
from acfun.libs.ffmpeg_progress_yield import FfmpegProgress
from acfun.source import scheme, domains, routes, apis, pagelets, pagelets_big, pagelets_normal, videoQualitiesRefer
from acfun.exceptions import *

__author__ = 'dolacmeo'


def match1(text, *patterns):
    """Scans through a string for substrings matched some patterns (first-subgroups only).

    Args:
        text: A string to be scanned.
        patterns: Arbitrary number of regex patterns.

    Returns:
        When only one pattern is given, returns a string (None if no match found).
        When more than one pattern are given, returns a list of strings ([] if no match found).
    """

    if len(patterns) == 1:
        pattern = patterns[0]
        match = re.search(pattern, text)
        if match:
            return match.group(1)
        else:
            return None
    else:
        ret = []
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                ret.append(match.group(1))
        return ret


def matchall(text, patterns):
    """Scans through a string for substrings matched some patterns.

    Args:
        text: A string to be scanned.
        patterns: a list of regex pattern.

    Returns:
        a list if matched. empty if not.
    """

    ret = []
    for pattern in patterns:
        match = re.findall(pattern, text)
        ret += match

    return ret


class B64s:
    STANDARD = b'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
    EN_TRANS = STANDARD
    DE_TRANS = STANDARD

    def __init__(self, s: [bytes, bytearray], n: [int, None] = None):
        self.raw = s
        if isinstance(n, int):
            n = n % 64
            new = self.STANDARD[n:] + self.STANDARD[:n]
            self.EN_TRANS = bytes.maketrans(self.STANDARD, new)
            self.DE_TRANS = bytes.maketrans(new, self.STANDARD)

    def b64encode(self):
        return base64.standard_b64encode(self.raw).translate(self.EN_TRANS)

    def b64decode(self):
        return base64.b64decode(self.raw.translate(self.DE_TRANS))


def danmaku2ass(client, folder_path: str, filenameId: str, vq: str = "720p", fontsize: int = 40):
    """
    https://github.com/niuchaobo/acfun-helper/blob/master/src/fg/modules/danmaku.js
    基础代码复刻自acfun助手中弹幕相关处理
    关于解决原代码中的弹幕重叠问题：
        0. 原弹幕数据要按时间进行排序
        1. 记录每条弹幕通道最后截止位置
        2. 如果同期所有通道已满，则减少弹幕停留时间(加速通过)

    :param client: acer.client
    :param folder_path: source path
    :param filenameId: ac_num
    :param vq: VideoQuality
    :return: ass file path
    :param fontsize: num px
    """

    # 检查路径
    assert os.path.isdir(folder_path) is True
    folder_name = os.path.basename(folder_path)
    video_data_path = os.path.join(folder_path, 'data', f"{filenameId}.json")
    danmaku_data_path = os.path.join(folder_path, 'data', f"{filenameId}.danmaku.json")
    assert all([os.path.isfile(video_data_path), os.path.isfile(danmaku_data_path)]) is True
    video_data = json.load(open(video_data_path, 'rb'))
    danmaku_data = json.load(open(danmaku_data_path, 'rb'))
    danmuMotionList = []
    if len(danmaku_data) == 0:
        return None

    thisVideoInfo = videoQualitiesRefer[vq]
    thisVideoWidth = thisVideoInfo['width']
    thisVideoHeight = thisVideoInfo['height']
    thisDuration = 10
    channelNum = math.floor(thisVideoWidth / fontsize)
    scriptInfo = "\n".join([
        "[Script Info]",
        f"; AcVid: {folder_name}",
        f"; StreamName: {video_data['title']}",
        f"Title: {folder_name} - {video_data['user']['name']} - {video_data['title']}",
        f"Original Script: {folder_name} - {video_data['user']['name']} - {video_data['title']}",
        "Script Updated By: acfunSDK转换",
        "ScriptType: v4.00+",
        "Collisions: Normal",
        f"PlayResX: {thisVideoWidth}",
        f"PlayResY: {thisVideoHeight}"
    ])
    styles = "\n".join([
        "[V4+ Styles]",
        "Format: " + ", ".join([
            'Name', 'Fontname', 'Fontsize', 'PrimaryColour', 'SecondaryColour', 'OutlineColour',
            'BackColour', 'Bold', 'Italic', 'Underline', 'StrikeOut', 'ScaleX', 'ScaleY',
            'Spacing', 'Angle', 'BorderStyle', 'Outline', 'Shadow', 'Alignment', 'MarginL',
            'MarginR', 'MarginV', 'Encoding']),
        "Style: " + ",".join([
            'Danmu', 'Microsoft YaHei', f'{fontsize}',
            '&H00FFFFFF', '&H00FFFFFF', '&H00000000', '&H00000000',
            '0', '0', '0', '0', '100', '100', '0', '0', '1', '1',
            '0', '2', '20', '20', '2', '0'])
    ])
    events = "\n".join([
        "[Events]",
        "Format: " + ", ".join([
            'Layer', 'Start', 'End', 'Style', 'Name',
            'MarginL', 'MarginR', 'MarginV', 'Effect', 'Text\n'])
    ])
    assData = list()
    screenChannel = [None for i in range(channelNum)]

    def timeProc(second, offset=0):
        second = second + offset
        minute = math.floor(second / 60)
        hours = math.floor(second / 60 / 60)
        minute = minute - hours * 60
        second = second - hours * 60 * 60 - minute * 60
        sec = second + offset
        return f"{hours:0>2}:{minute:0>2}:{sec:0>2.2f}"

    def choice_channel(startT, endT):
        # 按新时间移除频道占位
        empty = []
        for i, thisEnd in enumerate(screenChannel):
            if i in [0, 1]:
                continue
            elif thisEnd is None:
                empty.append(i)
            elif startT > thisEnd:
                screenChannel[i] = None
        # 无空位时返回空
        if len(empty) == 0:
            return None
        # 随机选择空位，记录结束时间，返回结果
        used = random.choice(empty)
        screenChannel[used] = endT
        return used

    for danmaku in danmaku_data:
        # 略过高级弹幕
        if danmaku['danmakuType'] != 0:
            continue
        # 弹幕挂载时间（文本）（弹幕左边界 接触到 视频的右边界）
        startTime = danmaku['position'] / 1000
        # 弹幕的长度
        danmakuLen = len(danmaku['body']) * fontsize
        danmakuLen_total = danmakuLen + thisVideoWidth
        # 运动到出界的时间点
        toLeftTime = startTime + thisDuration + (danmakuLen_total / thisVideoWidth)
        # 寻找频道
        danmaku_channel = choice_channel(startTime, toLeftTime)
        if danmaku_channel is None:  # 频道全满，加速通过
            toLeftTime -= int(thisDuration / 2)
            danmaku_channel = random.randint(2, channelNum)
        channelHeight = danmaku_channel * fontsize
        # 所有点位
        x1 = danmakuLen_total
        y1 = channelHeight
        x2 = - danmakuLen
        y2 = channelHeight
        dialogue = [
            "Dialogue: 0", timeProc(startTime), timeProc(toLeftTime),
            "Danmu", f"{danmaku['userId']}", "20", "20", "2", "",
            "{\\move(" + f"{x1}", f"{y1}", f"{x2}", f"{y2})" + "}" + f"{danmaku['body']}"
        ]
        assData.append(",".join(dialogue))
    events += "\n".join(assData)
    result = "\n\n".join([scriptInfo, styles, events])
    ass_path = os.path.join(folder_path, f"{filenameId}.ass")
    with open(ass_path, 'w', encoding="utf_8_sig") as ass_file:
        ass_file.write(result)
    ass_js_path = os.path.join(folder_path, 'data', f"{filenameId}.ass.js")
    ass_js_data = [
        "let assData=\"\" + \n",
        *[f"\"{x}\" + \n" for x in result.split('\n')],
        "\"\";"
    ]
    with open(ass_js_path, 'wb') as ass_js:
        ass_js.write("".join(ass_js_data).encode())
    return ass_path


def image_uploader(client, image_data: bytes, ext: str = 'jpeg'):
    token_req = client.post(apis['image_upload_gettoken'], data=dict(fileName=uuid4().hex.upper() + f'.{ext}'))
    token_data = token_req.json()
    assert token_data.get('result') == 0
    resume_req = client.get(apis['image_upload_resume'], params=dict(upload_token=token_data['info']['token']))
    resume_data = resume_req.json()
    assert resume_data.get('result') == 1
    fragment_req = client.post(apis['image_upload_fragment'], data=image_data,
                               params=dict(upload_token=token_data['info']['token'], fragment_id=0),
                               headers={"Content-Type": "application/octet-stream"})
    fragment_data = fragment_req.json()
    assert fragment_data.get('result') == 1
    complete_req = client.post(apis['image_upload_complete'],
                               params=dict(upload_token=token_data['info']['token'], fragment_count=1))
    complete_data = complete_req.json()
    assert complete_data.get('result') == 1
    result_req = client.post(apis['image_upload_geturl'], data=dict(token=token_data['info']['token']))
    result_data = result_req.json()
    assert result_data.get('result') == 0
    return result_data.get('url')


def get_usable_ffmpeg(cmd: [str, None] = None):
    cmds = ['ffmpeg', os.path.join(os.getcwd(), 'ffmpeg.exe')]
    if cmd is not None and os.path.isfile(cmd):
        cmds.append(cmd)
    for x in cmds:
        try:
            p = subprocess.Popen([x, '-version'], stdin=subprocess.DEVNULL,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = p.communicate()
            vers = str(out, 'utf-8').split('\n')[0].split()
            assert vers[0] == 'ffmpeg' and vers[2][0] > '0'
            return x
        except FileNotFoundError:
            continue
    return None


def acfun_video_downloader(client, data: dict,
                           save_path: [str, os.PathLike, None] = None, quality: [str, int, None] = 0):
    save_path = os.getcwd() if save_path is None else save_path
    quality = 0 if quality is None else quality
    quality_index, quality_text, filesize_bytes = -1, None, 0
    video_type, ac_num, part_num, ac_name, acfun_url = None, None, None, None, None
    # 获取视频编号名称等信息
    if "dougaId" in data:  # 视频类型
        video_type = "video"
        ac_num = data.get("dougaId")
        part_num = data.get("priority") + 1
        ac_name = f"ac{ac_num}"
        if part_num > 1:
            ac_name += f"_{part_num}"
        acfun_url = f"{routes['video']}{ac_name[2:]}"
    elif "bangumiId" in data:  # 番剧类型
        video_type = "bangumi"
        ac_num = data.get("bangumiId")
        part_num = data.get("priority") // 10
        item_id = data.get('itemId')
        ac_name = f"aa{ac_num}"
        if part_num > 1:
            ac_name += f"_36188_{item_id}"
        acfun_url = f"{routes['bangumi']}{ac_name[2:]}"
    else:
        raise Exception("error: video type not support")
    # 编码信息，视频尺寸
    video_quality = data['currentVideoInfo']['transcodeInfos']
    if isinstance(quality, int):
        if quality not in range(len(video_quality)):
            raise Exception('error: out of the quality length')
        quality_index = quality
        quality_text = video_quality[quality]['qualityType']
        filesize_bytes = video_quality[quality]['sizeInBytes']
    elif isinstance(quality, str):
        for i, q in enumerate(video_quality):
            if q['qualityType'] == quality:
                quality_index = i
                quality_text = q['qualityType']
                filesize_bytes = q['sizeInBytes']
    if quality_index == -1 or filesize_bytes == 0:
        raise Exception('error: selected quality not found')
    player_json = json.loads(data['currentVideoInfo']['ksPlayJson'])
    quality_data = player_json['adaptationSet'][0]['representation'][quality_index]
    m3u8_url = quality_data['url']
    url_parse = parse.urlsplit(m3u8_url)
    video_path = "/".join(url_parse.path.split('/')[:-1])
    video_base_path = f"{url_parse.scheme}://{url_parse.netloc}{video_path}/"
    m3u8_req = client.get(m3u8_url)
    # 保存m3u8文件
    os.makedirs(save_path, exist_ok=True)
    with open(os.path.join(save_path, f"{ac_name}[{quality_text}].m3u8"), 'w') as m3u8_file:
        for line in m3u8_req.text.split('\n'):
            if line.startswith('#EXT'):
                m3u8_file.write(line + "\n")
                continue
            m3u8_file.write(f"{video_base_path}{line}\n")
    # ffmpeg 下载
    video_save_path = os.path.join(save_path, f"{ac_name}[{quality_text}].mp4")
    ffmpeg_cmd = get_usable_ffmpeg()
    ffmpeg_params = [
        ffmpeg_cmd, '-y', '-i', m3u8_url,
        '-c', 'copy', '-bsf:a', 'aac_adtstoasc',
        '--', video_save_path
    ]
    ff = FfmpegProgress(ffmpeg_params)
    with alive_bar(100, title=f"{ac_name}", manual=True, force_tty=True) as bar:
        for progress in ff.run_command_with_progress():
            if progress > 0:
                bar(progress/100)
        bar(1)
    return os.path.isfile(video_save_path)


def downloader(client, src_url, fname: [str, None] = None, dest_dir: [str, None] = None, display: bool = True):
    if dest_dir is None:
        dest_dir = os.getcwd()
    elif os.path.isabs(dest_dir) is False:
        dest_dir = os.path.abspath(dest_dir)
    if not os.path.isdir(dest_dir):
        os.makedirs(dest_dir, exist_ok=True)
    if fname is None:
        fname = urlparse(src_url).path.split('/')[-1]
    fpath = os.path.join(dest_dir, fname)

    try:
        with open(fpath, 'wb') as download_file:
            with client.stream("GET", src_url) as response:
                if response.status_code // 100 != 2:
                    download_file.close()
                    os.remove(fpath)
                    return None
                total = int(response.headers.get("Content-Length", 0))
                total = None if total == 0 else total // 1024
                downloaded = 0
                with alive_bar(total, manual=False if total is None else True,
                               length=30, disable=not display,
                               title=fname, title_length=20, force_tty=True,
                               monitor=None if total is None else "{count}/{total} [{percent:.1%}]",
                               stats=False, elapsed_end=False) as progress:
                    for chunk in response.iter_bytes():
                        download_file.write(chunk)
                        if total is None:
                            progress(int(response.num_bytes_downloaded // 1024))
                        elif total == 0:
                            progress(int((response.num_bytes_downloaded - downloaded) // 1024))
                        else:
                            progress(downloaded / total)
                        downloaded = response.num_bytes_downloaded
                    if total is not None:
                        progress(1)
    except (httpx.ConnectError, httpx.ConnectTimeout, httpx.ReadTimeout):
        print("httpx.ConnectError:", src_url)
        os.remove(fpath)
        return None
    except KeyboardInterrupt:
        os.remove(fpath)
        raise KeyboardInterrupt

    if os.path.isfile(fpath) and os.path.exists(fpath):
        if '.' not in fname:
            kind = filetype.guess_extension(fpath)
            if kind is not None:
                new_fpath = ".".join([fpath, kind])
                shutil.move(fpath, new_fpath)
                return new_fpath
        return fpath
    return None


def thin_string(_string: str, no_break: bool = False):
    final_str = list()
    for line in _string.replace('\r', '').split('\n'):
        new_line = ' '.join(line.split()).strip()
        if len(new_line):
            final_str.append(new_line)
    if no_break is True:
        return " ".join(final_str)
    return " ↲ ".join(final_str)


def warp_mix_chars(_string: str, lens: int = 40, border: [tuple, None] = None):
    output = list()
    tmp_string = ""
    tmp_count = 0
    for i, _char in enumerate(_string):
        char_count = 2 if '\u4e00' <= _char <= '\u9fcc' else 1
        if tmp_count + char_count > lens:
            tmp_string += ' ' * (lens - tmp_count)
            output.append(tmp_string)
            tmp_string = ""
            tmp_count = 0
        tmp_string += _char
        tmp_count += char_count
    if tmp_count != 0:
        tmp_string += ' ' * (lens - tmp_count)
        output.append(tmp_string)
    if isinstance(border, tuple) and len(border) == 2:
        output = [f"{border[0]}{x}{border[1]}" for x in output]
    return output


def get_channel_info(html):
    rex = re.compile('\{subChannelId\:(\d+),subChannelName\:\"((?:(?!").)*)\"\}')
    result = rex.findall(html)
    if result is not None:
        return {"subChannelId": result[0][0], "subChannelName": result[0][1]}
    return {}


def ms2time(ms: int):
    d = timedelta(milliseconds=ms)
    return str(d).split('.')[0]


def get_page_pagelets(page_obj):
    data = list()
    for item in page_obj.select("[id^=pagelet_]"):
        data.append(item.attrs['id'])
    if len(data):
        data.append('footer')
    return data


def url_complete(url):
    if isinstance(url, str):
        if url.startswith('//'):
            url = f"https:{url}"
        elif not url.startswith('http'):
            url = f"{routes['index']}{url}"
    return url


class AcLink:

    def __init__(self, acer, url, title, container=None):
        self.acer = acer
        self.title = title
        self.url = url_complete(url)
        self.container = container

    def loading(self):
        pass

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

    def loading(self):
        pass

    def __repr__(self):
        show_link = f" >> {self.url}" if self.url else ""
        return f"AcImg({self.name}[{self.src}]{show_link})"

    def save_as(self, fname: [str, None] = None, dest_dir: [str, None] = None):
        return downloader(self.acer.client, self.url, fname, dest_dir)


class AcPagelet:
    pagelet_raw = None
    pagelet_id = None
    pagelet_obj = None
    pagelet_sp = (
        'pagelet_banner',
        'pagelet_top_area',
        'pagelet_monkey_recommend',
        'pagelet_live',
        'pagelet_spring_festival',
        'pagelet_list_banana',
        'pagelet_bangumi_list',
    )

    def __init__(self, acer, pagelet_data: [Tag, dict]):
        self.acer = acer
        self.pagelet_raw = pagelet_data
        if isinstance(pagelet_data, Tag):
            self.pagelet_id = pagelet_data.attrs['id']
            self.pagelet_obj = pagelet_data
            assert self.pagelet_id.startswith("pagelet_") or \
                   self.pagelet_id in ['footer']
        elif isinstance(pagelet_data, dict):
            self.pagelet_id = pagelet_data.get('id')
            self.pagelet_obj = Bs(pagelet_data.get('html', ""), "lxml")
        else:
            raise TypeError("pagelet_data allow bs4Tag or dict.")

    def _index_banner(self, obj=False):
        if self.pagelet_id != "pagelet_banner":
            return None
        data = dict()
        for rule in cssutils.parseString(self.pagelet_raw.get('styles', [])[0]):
            if isinstance(rule, cssutils.css.cssstylerule.CSSStyleRule) and \
                    rule.selectorText == ".page-top-banner .banner-pic":
                for pro in rule.style:
                    if pro.name == 'background-image':
                        data['image'] = pro.value[5:-2]
        data['url'] = self.pagelet_obj.select_one(".page-top-banner > a.banner-pic").attrs['href']
        data['title'] = self.pagelet_obj.select_one(".float-text").text
        if obj is True:
            return AcImage(self.acer, data['image'], data['url'], data['title'])
        return data

    def _index_top_area(self, obj=False):
        if self.pagelet_id != "pagelet_top_area":
            return None
        data = dict(slider=list(), items=list())
        for js_data in self.pagelet_raw.get('scripts', [])[0].split('\n'):
            if js_data.strip().startswith("window.sliderData = ["):
                data['slider'] = json.loads(js_data.strip()[20:-1])
        for video in self.pagelet_obj.select('a.recommend-video.log-item'):
            data['items'].append({
                'mediaid': video.attrs['data-mediaid'],
                'url': routes['video'] + video.attrs['data-mediaid'],
                'title': video.select_one('.video-title').text,
                'cover': video.select_one('img').attrs['src']
            })
        if obj is True:
            return dict(
                slider=[AcImage(
                    self.acer, s['image'], s['link'], s['title'],
                    self.acer.get(f"{routes['index']}{s['link']}")
                ) for s in data['slider']],
                items=[self.acer.AcVideo(v['mediaid'], dict(title=v['title'])) for v in data['items']]
            )
        return data

    def _index_monkey_recommend(self, obj=False):
        if self.pagelet_id != "pagelet_monkey_recommend":
            return None
        videos = list()
        for video in self.pagelet_obj.select(".monkey-recommend-videos > .video-list > .monkey-video"):
            videos.append({
                'mediaid': video.attrs['data-mediaid'],
                'url': routes['video'] + video.attrs['data-mediaid'],
                'title': video.select_one('.monkey-video-title').text,
                'infos': video.select_one('.monkey-video-title').attrs['title'].split('\r'),
                'cover': video.select_one('.monkey-video-cover').img.attrs['src'],
                'up': video.select_one('.monkey-up-name').attrs['title'],
                'up_url': video.select_one('.monkey-up-name').attrs['href'],
            })
        data = dict(items=videos)
        ad_img = self.pagelet_obj.select_one('.activity-box')
        data['ad'] = {
            'title': ad_img.attrs['data-title'],
            'url': ad_img.attrs['href'],
            'image': ad_img.img.attrs['src']
        }
        if obj is True:
            return dict(
                ad=AcImage(self.acer, data['ad']['image'], f"{data['ad']['url']}", data['ad']['title']),
                items=[
                    self.acer.AcVideo(v['mediaid'], dict(title=v['title'], user=dict(id=v['up_url'][3:], name=v['up'])))
                    for v in videos
                ]
            )
        return data

    def _index_live(self, obj=False):
        if self.pagelet_id != "pagelet_live":
            return None
        videos = list()
        for video in self.pagelet_obj.select(".live-module-videos > .video-list > .live-video"):
            videos.append({
                'liveid': video.attrs['data-liveid'],
                'url': routes['live'] + video.attrs['data-liveid'],
                'title': video.select_one('.live-video-title').text,
                'infos': video.select_one('.live-video-title').attrs['title'].split('\r'),
                'cover': video.select_one('.live-video-cover').img.attrs['src'],
                'up': video.select_one('.live-video-up-name').attrs['title'],
                'up_avatar': video.select_one('.live-video-avatar').img.attrs['src'],
            })
        data = dict(items=videos)
        ad_img = self.pagelet_obj.select_one('.activity-box')
        data['ad'] = {
            'title': ad_img.attrs['data-title'],
            'url': ad_img.attrs['href'],
            'image': ad_img.img.attrs['src']
        }
        if obj is True:
            return dict(
                ad=AcImage(self.acer, data['ad']['image'], f"{data['ad']['url']}", data['ad']['title']),
                items=[self.acer.AcLiveUp(v['liveid']) for v in videos]
            )
        return data

    def _index_spring_festival(self, obj=False):
        if self.pagelet_id != "pagelet_spring_festival":
            return None
        return None

    def _index_list_banana(self, obj=False):
        if self.pagelet_id != "pagelet_list_banana":
            return None
        data = dict(d1=list(), d3=list(), d7=list(), article=dict())
        for rank in [('d1', '.day-list'), ('d3', '.three-day-list'), ('d7', '.week-list')]:
            for video in self.pagelet_obj.select(f".rank-left > {rank[1]} > .banana-video"):
                data[rank[0]].append({
                    'mediaid': video.attrs['data-mediaid'],
                    'url': routes['video'] + video.attrs['data-mediaid'],
                    'title': video.select_one('.banana-video-title').text,
                    'infos': video.select_one('.banana-video-title').attrs['title'].split('\r'),
                    'cover': video.select_one('.banana-video-cover').img.attrs['src'],
                    'up': video.select_one('.banana-up-name').attrs['title'],
                    'up_url': video.select_one('.banana-up-name').attrs['href'],
                    'banana_count': video.select_one('.banana-count').text,
                })
        for article_tab in self.pagelet_obj.select('.rank-right .main-header-item'):
            tab_name = article_tab.select_one('.header-item-link').text
            tab_url = article_tab.select_one('.header-item-link').attrs['href']
            data['article'][tab_name] = dict(name=tab_name, url=tab_url, article=list())
            for index, article in enumerate(article_tab.select('.tab-main-content > li')):
                if index == 0:
                    this_article = {
                        'mediaid': article.attrs['data-mediaid'],
                        'url': routes['article'] + article.attrs['data-mediaid'],
                        'title': article.select_one('.main-content-block > a > p.block-title').text,
                        'infos': article.select_one('.main-content-block > a > p.block-title').attrs['title'].split(
                            '\r'),
                        'headimg': article.select_one('img.block-img').attrs['src'],
                        'up': article.select_one('span.block-up').a.attrs['title'],
                        'up_url': article.select_one('span.block-up').a.attrs['href'],
                        'comment_num': article.select_one('span.icon-comments').text
                    }
                else:
                    this_article = {
                        'mediaid': article.attrs['data-mediaid'],
                        'url': routes['article'] + article.attrs['data-mediaid'],
                        'title': article.a.text,
                        'infos': article.a.attrs['title'].split('\r'),
                    }
                data['article'][tab_name]['article'].append(this_article)
        if obj is True:
            obj_data = dict(d1=list(), d3=list(), d7=list(), article=dict())
            for rank in ['d1', 'd3', 'd7']:
                obj_data[rank] = [
                    self.acer.AcVideo(
                        v['mediaid'], dict(title=v['title'], user=dict(id=v['up_url'][3:], name=v['up'])))
                    for v in data[rank]
                ]
            for tab_name in data['article'].keys():
                obj_data['article'][tab_name] = [
                    self.acer.AcArticle(
                        a['mediaid'],
                        dict(title=a['title'], user=dict(id=a.get('up_url', '   ')[3:], name=a.get('up', ''))))
                    for a in data['article'][tab_name]['article']
                ]
            return obj_data
        return data

    def _index_bangumi_list(self, obj=False):
        if self.pagelet_id != "pagelet_bangumi_list":
            return None
        data = dict(schedule=list(), recommend=list(), anli=list())
        data['title'] = self.pagelet_obj.select_one('.area-header span.header-title').text
        data['icon'] = self.pagelet_obj.select_one('.area-header img.header-icon').attrs['src']
        data['url'] = routes['index'] + self.pagelet_obj.select_one('.header-right-more').attrs['href']
        if obj is True:
            data.update({
                'channel': self.acer.get(data['url']),
                'icon': AcImage(self.acer, data['icon'], data['url'], f"{data['title']}_icon")
            })
        for i, day in enumerate(self.pagelet_obj.select('.area-left .column-list .time-block')):
            day_list = list()
            for bangumi in day.select('.time-block .list-item'):
                if 'has-img' in bangumi.attrs['class']:
                    media_data = {
                        'mediaid': bangumi.attrs['data-mediaid'],
                        'albumid': bangumi.attrs['data-albumid'],
                        'url': routes['bangumi'] + bangumi.attrs['data-albumid'],
                        'cover': bangumi.a.img.attrs['src'],
                        'name': bangumi.select_one('a:nth-child(2) > b').text,
                        'recently': bangumi.p.text
                    }
                else:
                    media_data = {
                        'mediaid': bangumi.attrs['data-mediaid'],
                        'albumid': bangumi.attrs['data-albumid'],
                        'url': routes['bangumi'] + bangumi.attrs['data-albumid'],
                        'name': bangumi.a.b.text,
                        'recently': bangumi.a.p.text
                    }
                if obj is True:
                    day_list.append(self.acer.AcBangumi(media_data['mediaid']))
                else:
                    day_list.append(media_data)
            data['schedule'].append(day_list)
        for goood in self.pagelet_obj.select('.area-left .block-list .block-list-item'):
            media_data = {
                'mediaid': goood.attrs['data-mediaid'],
                'albumid': goood.attrs['data-albumid'],
                'url': routes['bangumi'] + goood.attrs['data-albumid'],
                'cover': goood.select_one('.block-img img').attrs['src'],
                'name': goood.select_one('.block-list-title > b > a').text,
                'follow': goood.select_one('.block-list-title > p > i.fr').text
            }
            if obj is True:
                data['recommend'].append(self.acer.AcBangumi(media_data['mediaid']))
            else:
                data['recommend'].append(media_data)
        for block in self.pagelet_obj.select('.area-right .season-rec'):
            media_data = {
                'mediaid': block.attrs['data-mediaid'],
                'albumid': block.attrs['data-albumid'],
                'url': routes['bangumi'] + block.attrs['data-albumid'],
                'cover': block.img.attrs['src']
            }
            if obj is True:
                data['anli'].append(self.acer.AcBangumi(media_data['mediaid']))
            else:
                data['anli'].append(media_data)
        return data

    def _index_pagelet_left_info(self, obj=False):
        data = dict(title=None, icon=None, links=list(), url=None)
        data['title'] = self.pagelet_obj.select_one('.module-left-header span.header-title').text
        data['icon'] = self.pagelet_obj.select_one('.module-left-header img.header-icon').attrs['src']
        for link in self.pagelet_obj.select('.link-container a'):
            href = ("" if link.attrs['href'].startswith('http') else routes['index']) + link.attrs['href']
            data['links'].append({'url': href, 'title': link.text})
        data['url'] = routes['index'] + self.pagelet_obj.select_one('.header-right-more').attrs['href']
        if obj is True:
            return {
                'channel': self.acer.get(data['url']),
                'links': [self.acer.get(x['url'], x['title']) for x in data['links']],
                'icon': AcImage(self.acer, data['icon'], data['url'], f"{data['title']}_icon")
            }
        return data

    def _index_pagelet_right_rank(self, obj=False):
        data = dict(rank=dict(d1=list(), d3=list(), d7=list()))
        for index, rank in enumerate(self.pagelet_obj.select('.list-content-videos')):
            for rank_item in rank.select('.log-item'):
                rank_type = f'd{"137"[index]}'
                if 'video-item-big' in rank_item['class']:
                    rank_data = {
                        'mediaid': rank_item.attrs['data-mediaid'],
                        'url': routes['video'] + rank_item.attrs['data-mediaid'],
                        'title': rank_item.select_one('.video-title').text,
                        'infos': rank_item.select_one('.video-title').attrs['title'].split('\r'),
                        'cover': rank_item.select_one('.block-left > a > img').attrs['src'],
                        'up': rank_item.select_one('.video-up').attrs['title'],
                        'up_url': rank_item.select_one('.video-up').attrs['href'],
                        'played_num': rank_item.select_one('.video-info > .icon-view-player').text,
                        'comment_num': rank_item.select_one('.video-info > .icon-comments').text
                    }
                else:
                    rank_data = {
                        'mediaid': rank_item.attrs['data-mediaid'],
                        'url': routes['video'] + rank_item.attrs['data-mediaid'],
                        'title': rank_item.a.text,
                        'infos': rank_item.a.attrs['title'].split('\r'),
                    }
                data['rank'][rank_type].append(rank_data)
        data['rank']['url'] = self.pagelet_obj.select_one('.ranked-list > .more').attrs['href']
        if obj is True:
            obj_data = dict(d1=list(), d3=list(), d7=list())
            for k in obj_data.keys():
                obj_data[k] = [
                    self.acer.AcVideo(v['mediaid'], dict(title=v['title']))
                    for v in data['rank'][k]
                ]
            return dict(rank=obj_data)
        return data

    def _index_pagelet_big(self, obj=False):
        data = dict(items=list())
        data['url'] = routes['index'] + self.pagelet_obj.select_one('.header-right-more').attrs['href']
        for video in self.pagelet_obj.select(".module-left > div:nth-child(2) > div"):
            if 'big-image' in video['class']:
                v_data = {
                    'mediaid': video.a.attrs['href'][5:],
                    'url': routes['index'] + video.a.attrs['href'],
                    'title': video.select_one('.title').text,
                    'infos': video.select_one('.title').attrs['title'].split('\r'),
                    'cover': video.select_one('.cover > img').attrs['src'],
                    'video_time': video.select_one('.video-time').text,
                }
            else:
                this_video = video.select_one('.normal-video')
                v_data = {
                    'mediaid': this_video.attrs['data-mediaid'],
                    'url': routes['video'] + this_video.attrs['data-mediaid'],
                    'title': this_video.select_one('.normal-video-title').text,
                    'infos': this_video.select_one('.normal-video-title').attrs['title'].split('\r'),
                    'cover': this_video.select_one('.normal-video-cover').img.attrs['src'],
                    'video_time': this_video.select_one('.video-time').text,
                    'played_num': this_video.select_one('.normal-video-info > .icon-view-player').text,
                    'danmu_num': this_video.select_one('.normal-video-info > .icon-danmu').text
                }
            if obj is True:
                data['items'].append(self.acer.AcVideo(v_data['mediaid'], dict(title=v_data['title'])))
            else:
                data['items'].append(v_data)
        data.update(self._index_pagelet_left_info(obj))
        data.update(self._index_pagelet_right_rank(obj))
        return data

    def _index_pagelet_normal(self, obj=False):
        data = dict(items=list())
        for video in self.pagelet_obj.select(".normal-video-container > .normal-video"):
            v_data = {
                'mediaid': video.attrs['data-mediaid'],
                'url': routes['video'] + video.attrs['data-mediaid'],
                'title': video.select_one('.normal-video-title').text,
                'infos': video.select_one('.normal-video-title').attrs['title'].split('\r'),
                'cover': video.select_one('.normal-video-cover').img.attrs['src'],
                'video_time': video.select_one('.video-time').text,
                'played_num': video.select_one('.normal-video-info > .icon-view-player').text,
                'danmu_num': video.select_one('.normal-video-info > .icon-danmu').text
            }
            if obj is True:
                data['items'].append(self.acer.AcVideo(v_data['mediaid'], dict(title=v_data['title'])))
            else:
                data['items'].append(v_data)
        data.update(self._index_pagelet_left_info(obj))
        data.update(self._index_pagelet_right_rank(obj))
        return data

    def _footer(self, obj=False):
        if self.pagelet_id != "footer":
            return None
        data = dict(links=dict(), infos=list(), copyright=dict())
        for link_group in self.pagelet_obj.select('.footer-nav > div'):
            for i, tag in enumerate(link_group.select('h5')):
                those_links = list()
                for link in link_group.select(f'p:nth-of-type({i + 1}) a'):
                    if 'href' in link.attrs:
                        this_link = {
                            'title': link.text,
                            'url': link.attrs['href']
                        }
                        if obj is True:
                            those_links.append(AcLink(self.acer, **this_link))
                        else:
                            those_links.append(this_link)
                    else:
                        this_link = {
                            'name': link.get_text(),
                            'src': link.select_one('img').attrs['src']
                        }
                        if obj is True:
                            those_links.append(AcImage(self.acer, **this_link))
                        else:
                            those_links.append(this_link)
                data['links'][tag.text] = those_links
        for info in self.pagelet_obj.select('.footer-link a'):
            this_link = {
                'title': info.text.strip(),
                'url': info.attrs['href']
            }
            if obj is True:
                data['infos'].append(AcLink(self.acer, **this_link))
            else:
                data['infos'].append(this_link)
        for ac in self.pagelet_obj.select_one('.footer-link > div:last-child').select('span'):
            if ": " in ac.text:
                k, v = ac.text.split(": ")
                data['copyright'][k] = v
        return data

    def to_dict(self, obj=False):
        if self.pagelet_id == 'footer':
            return self._footer(obj)
        elif self.pagelet_id in self.pagelet_sp:
            func_name = self.pagelet_id.replace("pagelet_", "_index_")
            return getattr(self, func_name)(obj)
        elif self.pagelet_id in pagelets_big:
            return self._index_pagelet_big(obj)
        elif self.pagelet_id in pagelets_normal:
            return self._index_pagelet_normal(obj)
        return None


class AcComment:
    sourceId = None
    hot_comments = list()
    root_comments = list()
    sub_comments = dict()
    commentIds = list()
    commentsMap = dict()

    def __init__(self, acer, sid: [str, int], stype: int = 3, referer: [str, None] = None):
        self.acer = acer
        self.sourceId = str(sid)
        self.sourceType = stype
        self.referer = referer or f"{routes['index']}"

    def __repr__(self):
        return f"AcComment([ac{self.sourceId}] Σ{len(self.root_comments)})"

    def _get_data(self, page: int = 1, api_name: str = 'comment'):
        assert api_name in ['comment', 'comment_floor']
        param = {
            "sourceId": self.sourceId,
            "sourceType": self.sourceType,
            "page": page,
            "pivotCommentId": 0,
            "newPivotCommentId": "",
            "t": str(time.time_ns())[:13],
            "supportZtEmot": True,
        }
        req = self.acer.client.get(apis[api_name], params=param)
        return req.json()

    def _get_sub(self, root_id, page: int = 1):
        param = {
            "sourceId": self.sourceId,
            "sourceType": self.sourceType,
            "rootCommentId": root_id,
            "page": page,
            "t": str(time.time_ns())[:13],
            "supportZtEmot": True
        }
        req = self.acer.client.get(apis['comment_subs'], params=param)
        return req.json()

    def get_all_comment(self):
        self.hot_comments = list()
        self.root_comments = list()
        self.sub_comments = dict()
        page = 1
        page_max = 10
        with alive_bar(100, manual=True, length=30, title="get all comments", force_tty=True, stats=False) as bar:
            while page <= page_max:
                api_data = self._get_data(page)
                if api_data.get('result') != 0:
                    print(api_data)
                    break
                self.hot_comments.extend(api_data.get('hotComments', []))
                self.root_comments.extend(api_data.get('rootComments', []))
                self.sub_comments.update(api_data.get('subCommentsMap', {}))
                page_max = api_data.get('totalPage', page)
                page = api_data.get('curPage', 1)
                page += 1
                bar(page / page_max)
            bar(1)

        for rid, sub_data in self.sub_comments.items():
            while sub_data['pcursor'] != "no_more":
                sub_page = self._get_sub(rid, sub_data['pcursor'])
                if 'subComments' not in sub_page:
                    sub_data['pcursor'] = "no_more"
                    break
                sub_data['subComments'].extend(sub_page['subComments'])
                if sub_page['curPage'] < sub_page['totalPage']:
                    sub_data['pcursor'] += 1
                else:
                    sub_data['pcursor'] = "no_more"
                time.sleep(0.1)

    def get_all_floors(self):
        first_page = self._get_data(1, 'comment_floor')
        self.commentIds = first_page['commentIds']
        self.commentsMap = first_page['commentsMap']
        page = first_page['curPage']
        page_max = first_page['totalPage']
        while page <= page_max:
            page += 1
            api_data = self._get_data(page, 'comment_floor')
            assert api_data['result'] == 0
            self.commentIds.extend(api_data['commentIds'])
            self.commentsMap.update(api_data['commentsMap'])
            time.sleep(0.5)

    @need_login
    def add(self, content: str, reply_id: [str, int, None] = None):
        form_data = {
            "sourceId": self.sourceId,
            "sourceType": self.sourceType,
            "content": content,
            "replyToCommentId": reply_id or "",
        }
        req = self.acer.client.post(apis['comment_add'], data=form_data,
                                    headers={'referer': self.referer})
        return req.json().get('result') == 0

    @need_login
    def delete(self, floor: int):
        this_comment = None
        for c in self.root_comments:
            if c.get('floor') == floor:
                this_comment = Comment(self.acer, c, self)
                break
        if this_comment is None:
            return False
        return this_comment.delete()

    def hot(self):
        datas = list()
        for c in self.hot_comments:
            datas.append(Comment(self.acer, c, self))
        return datas

    def list(self):
        datas = list()
        for c in self.root_comments:
            datas.append(Comment(self.acer, c, self))
        return datas

    def get(self, floor: int):
        for x in self.root_comments:
            if x['floor'] == floor:
                return Comment(self.acer, x, self)
        return None

    def find(self, cid: [int, str]):
        for x in self.root_comments:
            if x['commentId'] == int(cid):
                return Comment(self.acer, x, self)
        for x in self.sub_comments.values():
            for y in x.get('subComments', []):
                if y['commentId'] == int(cid):
                    return Comment(self.acer, y, self)
        return None


class Comment:
    data = dict()
    ac_num = None

    def __init__(self, acer, data: dict, main_obj: AcComment):
        self.acer = acer
        self.data = data
        self.ac_num = self.data.get('sourceId')
        self.main_obj = main_obj
        self.referer = self.main_obj.referer or f"{routes['index']}"

    def cdata(self, name):
        return self.data.get(name)

    def __repr__(self):
        content = self.data.get('content', '').replace('\r\n', '↲  ').replace('\n', '↲  ')
        return f"C([{self.cdata('commentId')}]#{self.cdata('floor')} {content} " \
               f"@{self.cdata('userName')}[{self.cdata('userId')}])"

    @property
    def api_data(self):
        return {
            "sourceId": self.data.get('sourceId'),
            "sourceType": self.data.get('sourceType'),
            "commentId": self.data.get('commentId'),
        }

    @need_login
    def like(self):
        if self.cdata('isLiked') is False:
            req = self.acer.client.post(apis['comment_like'], data=self.api_data, headers={'referer': self.referer})
            return req.json().get('result') == 0
        return True

    @need_login
    def unlike(self):
        if self.cdata('isLiked') is True:
            req = self.acer.client.post(apis['comment_unlike'], data=self.api_data, headers={'referer': self.referer})
            return req.json().get('result') == 0
        return True

    @need_login
    def delete(self):
        req = self.acer.client.post(apis['comment_delete'], data=self.api_data, headers={'referer': self.referer})
        return req.json().get('result') == 0


class AcDanmaku:
    ac_num = None
    vid = None
    danmaku_data = list()
    video_data = dict()

    def __init__(self, acer, video_data: dict):
        self.video_data = video_data
        self.ac_num = self.video_data.get('dougaId', self.video_data.get('bangumiId'))
        self.vid = self.video_data.get('currentVideoId', self.video_data.get('videoId'))
        self.acer = acer
        self._get_all_danmaku()

    def __repr__(self):
        return f"AcDanmaku([{self.vid}] Σ{len(self.danmaku_data)})"

    def _get_data(self, page=1, limit=200, sorttype=2, asc=True):
        param = {
            "resourceId": f"{self.vid}",
            "resourceType": "9",
            "enableAdvanced": True,
            "pcursor": f"{page}",
            "count": f"{limit}",
            "sortType": f"{sorttype}",
            "asc": asc,
        }
        req = self.acer.client.get(apis['danmaku'], params=param)
        return req.json()

    def _get_all_danmaku(self):
        self.danmaku_data = list()
        limit = 200
        page = 1
        more = 1
        while more > 0:
            api_data = self._get_data(page)
            total = api_data.get('totalCount', 1)
            self.danmaku_data.extend(api_data.get('danmakus', []))
            more = math.ceil(total / limit) - page
            page += 1

    def list(self):
        return [Danmaku(x, self.acer, self.video_data) for x in self.danmaku_data]

    @need_login
    def add(self, words, ms, color=16777215, mode=1, size=25):
        danmaku = {
            "size": size,  # 大* 中25 小16
            "mode": mode,
            "color": color,
            "position": ms,
            "body": words,
            "type": "bangumi" if "bangumiTitle" in self.video_data else "douga",
            "videoId": self.vid,
            "id": self.ac_num,
            "subChannelId": self.video_data.get('subChannelId'),
            "subChannelName": self.video_data.get('subChannelName'),
            "roleId": ""
        }
        req = self.acer.client.post(apis['danmaku_add'], data=danmaku, headers={"referer": f"{routes['index']}"})
        return req.json().get('result') == 0


class Danmaku:
    data = dict()
    video_data = dict()
    ac_num = None
    vid = None
    isLike = None

    def __init__(self, data: dict, acer=None, video_data: [dict, None] = None):
        self.data = data
        self.acer = acer
        if isinstance(video_data, dict):
            self.video_data = video_data
            self.vid = self.video_data.get('currentVideoId')
            self.ac_num = self.video_data.get('dougaId')

    def __repr__(self):
        return f"DM([{ms2time(self.position)}]#{self.danmakuId} {self.body} @{self.userId})"

    def __getattr__(self, item):
        if item in self.data.keys():
            return self.data.get(item)
        return super().__getattribute__(item)

    def get_up(self):
        return self.acer.ac_up({'id': self.userId}, self.acer)

    @need_login
    def like(self):
        req = self.acer.client.post(apis['danmaku_like'], params={"danmakuId": self.danmakuId})
        self.isLike = req.json().get('result') == 0
        return self.isLike is True

    @need_login
    def like_cancel(self):
        req = self.acer.client.post(apis['danmaku_like_cancel'], params={"danmakuId": self.danmakuId})
        self.isLike = not (req.json().get('result') == 0)
        return self.isLike is False

    @need_login
    def block_words(self, word=None):
        req = self.acer.client.post(apis['danmaku_block_add'], params={
            "blockWordsType": 1,
            "blockWords": word or self.body
        })
        return req.json().get('result') == 0

    @need_login
    def block_acer(self):
        req = self.acer.client.post(apis['danmaku_block_add'], params={
            "blockWordsType": 2,
            "blockWords": self.userId
        })
        return req.json().get('result') == 0

    @need_login
    def block_words_delete(self):
        req = self.acer.client.post(apis['danmaku_block_delete'], params={
            "blockWordsType": 1,
            "blockWordsList": self.body
        })
        return req.json().get('result') == 0

    @need_login
    def block_acer_delete(self):
        req = self.acer.client.post(apis['danmaku_block_delete'], params={
            "blockWordsType": 2,
            "blockWordsList": self.userId
        })
        return req.json().get('result') == 0

    @need_login
    def report(self):
        req = self.acer.client.post(apis['danmaku_block_delete'], params={
            "reportedUserId": self.userId,
            "danmakuId": self.danmakuId,
            "body": self.body,
            "type": "douga",
            "id": self.ac_num,
            "videoId": self.vid,
            "subChannelId": self.video_data.get('channel', {}).get('id'),
            "subChannelName": self.video_data.get('channel', {}).get('name'),
        })
        return req.json().get('result') == 0


class Message:
    intro = None
    create_at = None
    whom = None
    raw_data = None
    raw_link = None

    def __init__(self, acer, **kwargs):
        self.acer = acer
        self.raw_data = kwargs
        self.raw_link = kwargs.get('content_url')
        self.intro = kwargs.get('intro')
        self.create_at = kwargs.get('create_at')
        if 'uid' in kwargs:
            self.whom = {'userId': kwargs.get('uid'), 'name': kwargs.get('username')}

    def __repr__(self):
        return f"AcMsg({self.intro})"

    def user(self):
        if self.whom is None:
            return None
        return self.acer.AcUp(self.whom)


class ReplyMsg(Message):

    def __init__(self, acer, **kwargs):
        self.content_title = kwargs.get('content_title', '')
        self.replied = kwargs.get('replied', '')
        self.content = kwargs.get('content', '')
        self.ncid = kwargs.get('ncid', '')
        self.username = kwargs.get('username', '')
        super().__init__(acer, **kwargs)

    def __repr__(self):
        return f"AcReply({self.content_title}—— {self.content} @{self.username})"

    def content(self):
        return self.acer.get(self.raw_data.get('content_url'))

    def replay(self):
        comments = self.content().comment()
        return comments.find(self.raw_data.get('ncid'))


class LikeMsg(ReplyMsg):

    def __init__(self, acer, **kwargs):
        super().__init__(acer, **kwargs)

    def __repr__(self):
        return f"AcLike({self.replied} | @{self.username})"


class AtMsg(ReplyMsg):

    def __init__(self, acer, **kwargs):
        super().__init__(acer, **kwargs)

    def __repr__(self):
        return f"AcMsg({self.raw_link}#ncid={self.ncid} | @{self.username})"


class GiftMsg(Message):
    banana = 0

    def __init__(self, acer, **kwargs):
        self.content_title = kwargs.get('content_title', '')
        self.username = kwargs.get('username', '')
        self.banana = kwargs.get('banana', 0)
        super().__init__(acer, **kwargs)

    def __repr__(self):
        return f"AcGift({self.content_title} | 🍌x{self.banana} @{self.username})"


class NoticeMsg(Message):

    def __init__(self, acer, **kwargs):
        self.content_title = kwargs.get('content_title', '')
        super().__init__(acer, **kwargs)

    def __repr__(self):
        return f"AcNotice({self.content_title} >>> {self.raw_link})"


class SystemMsg(Message):
    classify = None

    def __init__(self, acer, **kwargs):
        super().__init__(acer, **kwargs)

    def __repr__(self):
        if 'up' in self.raw_data and '关注了你' in self.raw_data.get('intro', ''):
            link = self.raw_data.get('up', [])
            return f"AcFans(+1 | @{link[0]})"
        elif 'video' in self.raw_data and '已通过审核' in self.raw_data.get('intro', ''):
            link = self.raw_data.get('video', [])
            return f"AcPass({link[0]} 已通过审核)"
        elif 'article' in self.raw_data and '已通过审核' in self.raw_data.get('intro', ''):
            link = self.raw_data.get('article', [])
            return f"AcPass({link[0]} 已通过审核)"
        elif '有人收藏了你的' in self.raw_data.get('intro', ''):
            if 'video' in self.raw_data:
                link = self.raw_data.get('video', [])
            elif 'article' in self.raw_data:
                link = self.raw_data.get('article', [])
            else:
                return f"AcMsg({self.intro})"
            return f"AcStar(+1 | {link[0]})"
        return f"AcMsg({self.intro})"


class AcMessage:
    req_count = 0

    def __init__(self, acer):
        self.acer = acer

    @property
    def unread(self):
        if self.acer.is_logined is False:
            return None
        api_req = self.acer.client.get(apis['unread'])
        api_data = api_req.json()
        if api_data.get('result') != 0:
            return None
        return api_data.get("unReadCount")

    def _get_msg_api(self, vid: str = '', page: int = 1):
        vids = ['', 'like', 'atmine', 'gift', 'sysmsg', 'resmsg']
        assert vid in vids
        self.req_count += 1
        param = {
            "quickViewId": 'upCollageMain',
            "reqID": self.req_count,
            "ajaxpipe": 1,
            "pageNum": page,
            "t": str(time.time_ns())[:13],
        }
        api_req = self.acer.client.get(apis['message'] + vid, params=param)
        if api_req.text.endswith("/*<!-- fetch-stream -->*/"):
            api_data = json.loads(api_req.text[:-25])
            page_obj = Bs(api_data.get('html', ''), 'lxml')
        else:
            return None
        item_data = list()
        total = str(page_obj.select_one('#listview').attrs['totalcount'])
        for item in page_obj.select('#listview > ul,.main-block-msg-item'):
            if vid == '':
                main_url = scheme + ':' + item.select_one('.intro').a.attrs['href']
                reply_url = item.select_one('a.msg-reply').attrs['href']
                item_data.append({
                    'content_url': main_url,
                    'content_title': item.select_one('.intro').a.text.strip(),
                    'replied': item.select_one('.msg-replied .inner').text.strip().replace('\xa0', ' '),
                    'uid': item.select_one('.titlebar .name').attrs['href'][17:],
                    'username': item.select_one('.titlebar .name').text,
                    'create_at': item.select_one('.titlebar .time').text.strip(),
                    'ncid': reply_url.split('#ncid=')[1],
                    'content': item.select_one('.msg-reply .inner').text.strip().replace('\xa0', ' '),
                    'intro': item.select_one('.content .intro').text.strip(),
                })
            elif vid == 'like':
                this_url = item.select_one('a.replied').attrs['href'].split('#')
                main_url = scheme + ':' + this_url[0]
                item_data.append({
                    'content_url': main_url,
                    'replied': item.select_one('.clamp-text .inner').text.strip().replace('\xa0', ' '),
                    'uid': item.select_one('.titlebar .name').attrs['href'][17:],
                    'username': item.select_one('.titlebar .name').text,
                    'ncid': this_url[1][5:],
                    'create_at': item.select_one('.titlebar span.time').text.strip(),
                    'intro': item.select_one('.titlebar').text.strip(),
                })
            elif vid == 'atmine':
                this_url = item.select_one('.content .msg-text').attrs['href']
                item_data.append({
                    'content_url': scheme + ':' + this_url.split('#')[0],
                    'ncid': this_url.split('#ncid=')[1],
                    'uid': item.select_one('.avatar-section').attrs['href'][17:],
                    'username': item.select_one('.titlebar-container .name').text,
                    'create_at': item.select_one('.titlebar-container span.time').text.strip(),
                    'intro': item.select_one('.titlebar-container .intro').text.strip(),
                })
            elif vid == 'gift':
                if 'moment-gift' in item.attrs['class']:
                    this_url = item.select_one('.msg-content').a.attrs['href']
                    intro = thin_string(item.select_one('.msg-content').text)
                    item_data.append({
                        'classify': 'moment',
                        'content_url': scheme + ':' + this_url,
                        'content_title': '动态',
                        'uid': item.select_one('.avatar-section').attrs['href'][17:],
                        'username': item.select_one('.content .name').text,
                        'create_at': item.select_one('.content span.time').text.strip(),
                        'intro': intro,
                        'banana': int(re.findall('(\d)根香蕉', intro)[0])
                    })
                else:
                    acer_url = item.select_one('p a:nth-of-type(1)')
                    this_url = item.select_one('p a:nth-of-type(2)')
                    intro = thin_string(item.select_one('p').text)
                    item_data.append({
                        'classify': 'content',
                        'content_url': scheme + ':' + this_url.attrs['href'],
                        'content_title': this_url.text,
                        'uid': acer_url.attrs['href'][17:],
                        'username': acer_url.text,
                        'create_at': item.select_one('.msg-item-time').text.strip(),
                        'intro': intro,
                        'banana': int(re.findall('(\d)根香蕉', intro)[0])
                    })
            elif vid == 'sysmsg':
                this_title = item.select_one('div:nth-of-type(1)').text.strip()
                this_content = item.select_one('div:nth-of-type(2)').get_text("|", strip=True)
                this_content = "\n".join([text for text in this_content.split("|") if not text.startswith('http')])
                this_content = re.sub('(>{2,})', '', this_content)
                this_link = item.select_one('div:nth-of-type(2)').a.attrs['href']
                item_data.append({
                    'content_url': this_link,
                    'content_title': this_title,
                    'create_at': item.select_one('.msg-item-time').text.strip(),
                    'intro': thin_string(this_content),
                })
            elif vid == 'resmsg':
                intro = item.select_one('p:nth-of-type(1)').text.strip()
                links = dict()
                for link in item.select('a'):
                    url_str = link.attrs['href']
                    if not url_str.startswith('http'):
                        url_str = scheme + ':' + url_str
                    for link_name in ['video', 'article', 'album', 'bangumi', 'up', 'live']:
                        if url_str.startswith(routes[link_name]) and link_name not in links:
                            links[link_name] = [link.text, url_str]
                item_data.append({
                    'create_at': item.select_one('p.msg-item-time').text.strip(),
                    'intro': thin_string(intro, True),
                    **links
                })
        return item_data, total

    def reply(self, page: int = 1, obj: bool = False):
        api_data, total = self._get_msg_api('', page)
        if obj is True:
            return [ReplyMsg(self, **i) for i in api_data]
        return api_data

    def like(self, page: int = 1, obj: bool = False):
        api_data, total = self._get_msg_api('like', page)
        if obj is True:
            return [LikeMsg(self, **i) for i in api_data]
        return api_data

    def at(self, page: int = 1, obj: bool = False):
        api_data, total = self._get_msg_api('atmine', page)
        if obj is True:
            return [AtMsg(self, **i) for i in api_data]
        return api_data

    def gift(self, page: int = 1, obj: bool = False):
        api_data, total = self._get_msg_api('gift', page)
        if obj is True:
            return [GiftMsg(self, **i) for i in api_data]
        return api_data

    def notice(self, page: int = 1, obj: bool = False):
        api_data, total = self._get_msg_api('sysmsg', page)
        if obj is True:
            return [NoticeMsg(self, **i) for i in api_data]
        return api_data

    def system(self, page: int = 1, obj: bool = False):
        api_data, total = self._get_msg_api('resmsg', page)
        if obj is True:
            return [SystemMsg(self, **i) for i in api_data]
        return api_data
