# coding=utf-8
import json
import time
from bs4 import BeautifulSoup as Bs
from bs4.element import Tag
from acfunsdk.source import routes, pagelets_from_page, pagelets_from_api, pagelets_big, pagelets_normal
from acfunsdk.page.utils import get_page_pagelets, match1
from .extra import AcImage, AcLink

__author__ = 'dolacmeo'


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
        banner_css_text = "\n".join(self.pagelet_raw.get('styles', [])).replace("\n", "")
        banner_css = match1(banner_css_text, r"\.page-top-banner \.banner-pic \{(?P<banner>[^}]*)}")
        assert banner_css is not None
        banner_image = match1(banner_css, r"background-image: url\('(?P<image>[^)]*)'\);")
        assert banner_image is not None
        data['image'] = banner_image
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
        ads = self.pagelet_obj.select(".normal-ad-link")
        if len(ads):
            data['ads'] = list()
        for ad in ads:
            data['ads'].append({
                "url": routes['index'] + ad.attrs['href'],
                "title": ad.attrs['data-title'],
                "image": ad.select_one('img').attrs['src']
            })
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


class AcIndex:
    index_obj = None
    index_pagelets = []
    nav_data = dict()

    def __init__(self, acer=None):
        self.acer = acer
        self._get_index()

    def _get_index(self):
        req = self.acer.client.get(routes['index'])
        self.index_obj = Bs(req.text, 'lxml')
        self.index_pagelets = get_page_pagelets(self.index_obj)

    def _get_pagelet_inner(self, area: [str, None] = None):
        datas = dict()
        for js in self.index_obj.select("script"):
            if js.text.startswith("bigPipe.onPageletArrive"):
                data = json.loads(js.text[24:-2])
                datas[data['id']] = data
        datas['footer'] = self.index_obj.select_one('#footer')
        if isinstance(area, str):
            return datas.get(area)
        return datas

    def _get_pagelet_api(self, area):
        assert area in pagelets_from_api
        param = {
            "pagelets": area, "reqID": 0, "ajaxpipe": 1,
            "t": str(time.time_ns())[:13]
        }
        req = self.acer.client.get(routes['index'] + '/', params=param)
        if req.text.endswith("/*<!-- fetch-stream -->*/"):
            return json.loads(req.text[:-25])
        return req.json()

    def nav_list(self):
        navs = list()
        for cid in self.acer.nav_data.keys():
            navs.append(self.acer.AcChannel(cid))
        return navs

    def get(self, area: str, obj=False):
        if area != 'footer' and not area.startswith("pagelet_"):
            area = "pagelet_" + area
        if area in pagelets_from_page:
            raw_data = self._get_pagelet_inner(area)
        elif area in pagelets_from_api:
            raw_data = self._get_pagelet_api(area)
        else:
            raise ValueError('area not support')
        acp = AcPagelet(self.acer, raw_data)
        return acp.to_dict(obj)
