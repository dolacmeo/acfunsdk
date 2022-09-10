# coding=utf-8
import re
import html
import json
import textwrap
from bs4 import BeautifulSoup as Bs
from acfunsdk.source import routes, apis
from acfunsdk.page.utils import warp_mix_chars, get_page_pagelets, match1
from acfunsdk.saver import ArticleSaver

__author__ = 'dolacmeo'


class AcArticle:
    ac_num = None
    page_obj = None
    page_pagelets = []
    article_data = dict()
    console_width = 80
    is_404 = False

    def __init__(self, acer, ac_num: [str, int], article_data: [dict, None] = None):
        if isinstance(ac_num, str) and ac_num.startswith('ac'):
            ac_num = ac_num[2:]
        self.ac_num = str(ac_num)
        self.referer = f"{routes['article']}{ac_num}"
        self.acer = acer
        if isinstance(article_data, dict):
            self.article_data = article_data
        self.loading()

    def __repr__(self):
        if self.is_404 is True:
            return f"AcArticle([ac{self.ac_num}] 404)"
        title = self.article_data.get('contentTitle', self.article_data.get('title', ""))
        user_name = self.article_data.get('user', {}).get('name', "") or self.article_data.get('user', {}).get('id', "")
        user_txt = "" if len(user_name) == 0 else f" @{user_name}"
        return f"AcArticle([ac{self.ac_num}]{title}{user_txt})".encode(errors='replace').decode()

    @property
    def share_url(self):
        return self.referer

    def loading(self):
        req = self.acer.client.get(routes['article'] + self.ac_num)
        self.is_404 = req.status_code // 100 != 2
        if self.is_404:
            return None
        self.page_obj = Bs(req.text, 'lxml')
        json_text = match1(req.text, r"(?s)articleInfo\s*=\s*(\{.*?\});")
        self.article_data = json.loads(json_text)
        self.page_pagelets = get_page_pagelets(self.page_obj)

    def saver(self, dest_path=None):
        return ArticleSaver(self.acer, self, dest_path)

    def recommends(self):
        articles = list()
        for item in self.page_obj.select('#main > section.area > .content > .fr > .contribution.weblog-item'):
            this_url = item.select_one('.contb-title a').attrs['href']
            ac_num = this_url[5:]
            data = {
                'title': item.select_one('.contb-title').a.text,
                'shareUrl': routes['share'] + ac_num,
                'viewCount': item.select_one('.contb-count .view-count span.count').text,
                'commentCount': item.select_one('.contb-count .comm-count span.count').text,
                'user': self.article_data.get('user', {})
            }
            articles.append(self.acer.ac_article(ac_num, self.acer, data))
        return articles

    def infos(self):
        if len(self.article_data.keys()) == 0:
            self.loading()
        return self.article_data

    def content(self, num: [int, None] = None):
        show_text = list()
        show_text.extend(textwrap.wrap(self.article_data['title'], 80))
        show_text.extend(textwrap.wrap(self.article_data['description'], 80))
        show_text.append("*" * 80)

        def html2console(data, width=80):
            lines = list()
            page_raw = re.sub('\[emot=acfun,\d+/]', '', data.get('content', ''))
            page_obj = Bs(html.unescape(page_raw), 'lxml')
            for tag in page_obj.select('p,hr'):
                image = tag.select_one('img')
                br = tag.select_one('br')
                if 'hr' in tag.name:
                    lines.append('-' * width)
                elif image is not None:
                    lines.append(f"![ac{self.ac_num}_image]({image.attrs['src']})")
                elif br is not None:
                    lines.append(' ' * width)
                else:
                    this_text = tag.get_text(strip=True)
                    lines.extend(warp_mix_chars(this_text, width))
            return lines

        parts = self.article_data.get('parts', [])
        if len(parts) == 1:
            part_lines = html2console(parts[0])
            show_text.extend(part_lines)
        elif isinstance(num, int) and num in range(len(parts)):
            part_lines = html2console(parts[num])
            show_text.extend(part_lines)
        else:
            for part in parts:
                show_text.append("*" * 80)
                part_lines = html2console(part)
                show_text.extend(part_lines)
        show_text.append("=" * 80)
        return "\n".join(show_text)

    def up(self):
        if len(self.article_data.keys()) == 0:
            self.loading()
        return self.acer.ac_up(self.article_data.get('user', {}), self.acer)

    def comment(self):
        if len(self.article_data.keys()) == 0:
            self.loading()
        return self.acer.AcComment(self.ac_num, 1, self.referer)

    def like(self):
        return self.acer.like(self.ac_num, 3)

    def like_cancel(self):
        return self.acer.like_cancel(self.ac_num, 3)

    def favorite_add(self):
        return self.acer.favourite.add(self.ac_num, 3)

    def favorite_cancel(self):
        return self.acer.favourite.cancel(self.ac_num, 3)

    def banana(self, count: int):
        return self.acer.throw_banana(self.ac_num, 3, count)
