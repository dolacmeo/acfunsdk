# coding=utf-8
import re
import os
import time
import math
import json
import base64
import shutil
import cssutils
import filetype
from uuid import uuid4
from urllib.parse import urlparse
from bs4 import BeautifulSoup as Bs
from bs4.element import Tag
from datetime import timedelta
from alive_progress import alive_bar
from acfun.source import scheme, domains, routes, apis, pagelets, pagelets_big, pagelets_normal
from acfun.exceptions import *

__author__ = 'dolacmeo'


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


def image_uploader(client, image_data: bytes, ext: str = 'jpeg'):
    token_req = client.post(apis['image_upload_gettoken'], data=dict(fileName=uuid4().hex.upper()+f'.{ext}'))
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


def downloader(client, src_url, fname: [str, None] = None, dest_dir: [str, None] = None):
    if dest_dir is None:
        dest_dir = os.getcwd()
    elif os.path.isabs(dest_dir) is False:
        dest_dir = os.path.abspath(dest_dir)
    if not os.path.isdir(dest_dir):
        os.makedirs(dest_dir)
    if fname is None:
        fname = urlparse(src_url).path.split('/')[-1]
    fpath = os.path.join(dest_dir, fname)

    with open(fpath, 'wb') as download_file:
        with client.stream("GET", src_url) as response:
            total = int(response.headers["Content-Length"])
            if total == 0:
                return False
            with alive_bar(total // 1024, manual=True, length=30,
                           title=fname, title_length=20, force_tty=True,
                           monitor="{count}/{total} [{percent:.1%}]",
                           stats=False, elapsed_end=False) as progress:
                for chunk in response.iter_bytes():
                    download_file.write(chunk)
                    downloaded = response.num_bytes_downloaded
                    progress(downloaded / total)
                progress(1)

    if os.path.isfile(fpath) and os.path.exists(fpath):
        if '.' not in fname:
            kind = filetype.guess_extension(fpath)
            if kind is not None:
                new_fpath = ".".join([fpath, kind])
                shutil.move(fpath, new_fpath)
                return new_fpath
        return fpath
    return False


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
    return data


class AcLink:

    def __init__(self, acer, url, title, container=None):
        self.acer = acer
        self.title = title
        self.url = url
        self.container = container

    def loading(self):
        pass

    def __repr__(self):
        show_link = f" >> {self.url}" if self.url else ""
        return f"AcLink({self.title}{show_link})"


class AcImage:

    def __init__(self, acer, src, url=None, name=None, container=None):
        self.acer = acer
        self.src = src
        self.name = name
        self.url = url
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
                    self.acer,
                    s['image'],
                    s['link'] if s['link'].startswith("http") else f"{routes['index']}{s['link']}",
                    s['title'],
                    self.acer.get(s['link'] if s['link'].startswith("http") else f"{routes['index']}{s['link']}")
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
                ad=AcImage(self.acer, data['ad']['image'], f"{routes['index']}{data['ad']['url']}",
                           data['ad']['title']),
                items=[
                    self.acer.AcVideo(v['mediaid'], dict(title=v['title'], user=dict(id=v['up_url'][3:], name=v['up'])))
                    for v in videos
                ]
            )
        return data

    def _index_live(self, obj=False):  # todo 未完成直播对象
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

    def _index_bangumi_list(self, obj=False):  # todo 未完成番剧对象
        if self.pagelet_id != "pagelet_bangumi_list":
            return None
        data = dict(schedule=list(), recommend=list(), anli=list())
        data['title'] = self.pagelet_obj.select_one('.area-header span.header-title').text
        data['icon'] = self.pagelet_obj.select_one('.area-header img.header-icon').attrs['src']
        data['url'] = routes['index'] + self.pagelet_obj.select_one('.header-right-more').attrs['href']
        for i, day in enumerate(self.pagelet_obj.select('.area-left .column-list .time-block')):
            day_list = list()
            for bangumi in day.select('.time-block .list-item'):
                if 'has-img' in bangumi.attrs['class']:
                    media_data = {
                        'mediaid': bangumi.attrs['data-mediaid'],
                        'albumid': bangumi.attrs['data-albumid'],
                        'url': routes['anime'] + bangumi.attrs['data-albumid'],
                        'cover': bangumi.a.img.attrs['src'],
                        'name': bangumi.select_one('a:nth-child(2) > b').text,
                        'recently': bangumi.p.text
                    }
                else:
                    media_data = {
                        'mediaid': bangumi.attrs['data-mediaid'],
                        'albumid': bangumi.attrs['data-albumid'],
                        'url': routes['anime'] + bangumi.attrs['data-albumid'],
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
                'url': routes['anime'] + goood.attrs['data-albumid'],
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
                'url': routes['anime'] + block.attrs['data-albumid'],
                'cover': block.img.attrs['src']
            }
            if obj is True:
                data['anli'].append(self.acer.AcBangumi(media_data['mediaid']))
            else:
                data['anli'].append(media_data)
        return data

    def _index_pagelet_left_info(self, obj=False):  # todo 未完成栏目对象
        data = dict(title=None, icon=None, links=list(), url=None)
        data['title'] = self.pagelet_obj.select_one('.module-left-header span.header-title').text
        data['icon'] = self.pagelet_obj.select_one('.module-left-header img.header-icon').attrs['src']
        for link in self.pagelet_obj.select('.link-container > a'):
            data['links'].append({
                'url': routes['index'] + link.attrs['href'],
                'title': link.text
            })
        data['url'] = routes['index'] + self.pagelet_obj.select_one('.header-right-more').attrs['href']
        if obj is True:
            return {
                'channel': self.acer.get(data['url']),
                'links': [self.acer.get(x['url']) for x in data['links']]
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
        data = dict(items=list(), links=list())
        data['url'] = routes['index'] + self.pagelet_obj.select_one('.header-right-more').attrs['href']
        for link in self.pagelet_obj.select('.link-container > a'):
            this_link = {'url': routes['index'] + link.attrs['href'], 'title': link.text}
            if obj is True:
                data['links'].append(AcLink(self.acer, this_link['url'], this_link['title']))
            else:
                data['links'].append(this_link)
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

    def __init__(self, acer, sid: [str, int], stype: int = 3, referer: [str, None] = None):
        self.acer = acer
        self.sourceId = str(sid)
        self.sourceType = stype
        self.referer = referer or f"{routes['index']}"

    def __repr__(self):
        return f"AcComment([ac{self.sourceId}] Σ{len(self.root_comments)})"

    def _get_data(self, page=1):
        param = {
            "sourceId": self.sourceId,
            "sourceType": self.sourceType,
            "page": page,
            "pivotCommentId": 0,
            "newPivotCommentId": "",
            "t": str(time.time_ns())[:13],
            "supportZtEmot": True,
        }
        req = self.acer.client.get(apis['comment'], params=param)
        return req.json()

    def get_all_comment(self):
        self.hot_comments = list()
        self.root_comments = list()
        self.sub_comments = dict()
        page = 1
        page_max = 2
        while page <= page_max:
            api_data = self._get_data(page)
            if api_data.get('result') != 0:
                break
            self.hot_comments.extend(api_data.get('hotComments', []))
            self.root_comments.extend(api_data.get('rootComments', []))
            self.sub_comments.update(api_data.get('subCommentsMap', {}))
            page_max = api_data.get('totalPage', page)
            page = api_data.get('curPage', 1)
            page += 1

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

    def to_json(self, save_path=None):
        if save_path is None:
            return self.danmaku_data
        danmaku_text = json.dumps(self.danmaku_data, ensure_ascii=False)
        with open(save_path, 'w') as dm_json:
            dm_json.write(danmaku_text)
        return True


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






