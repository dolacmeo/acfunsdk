#!/usr/bin/env python

__all__ = ['douyin_download_by_url']

from ..common import *
#import re
#import json
#from urllib.parse import unquote

def douyin_download_by_url(url, **kwargs):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0',
        'Accept-Encoding': 'gzip, deflate',
        'Accept': '*/*',
        'Connection': 'keep-alive'
    }

    content = get_content(url, headers=headers)
    # TODO: to get the real content
    # compute __ac_nonce and __ac_signature
    # and pass them together with ttwid in cookies

    #data = r1(r'<script id=\"RENDER_DATA\" type=\"application/json\">(.*?)</script>', content)
    return ###


    # The video player and video source are rendered client-side, the data
    # contains in a <script id="RENDER_DATA" type="application/json"> tag
    # quoted, unquote the whole page content then search using regex with
    # regular string.
    page_content = unquote(page_content)
    title = re.findall(r'"desc":"([^"]*)"', page_content)[0].strip()
    video_format = 'mp4'
    # video URLs are in this pattern {"src":"THE_URL"}, in json format
    urls_pattern = r'"playAddr":(\[.*?\])'
    urls = json.loads(re.findall(urls_pattern, page_content)[0])
    video_url = 'https:' + urls[0]['src']
    size = url_size(video_url, faker=True)
    print_info(
        site_info='douyin.com', title=title,
        type=video_format, size=size
    )
    if not kwargs['info_only']:
        download_urls(
            urls=[video_url], title=title, ext=video_format, total_size=size,
            faker=True,
            **kwargs
        )


download = douyin_download_by_url
download_playlist = playlist_not_supported('douyin')
