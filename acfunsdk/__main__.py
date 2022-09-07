# coding=utf-8
import os
import sys
import time
import click
import httpx
import keyboard
from climage.climage import _toAnsi
from climage.climage import _color_types
from io import BytesIO
from PIL import Image
from urllib import parse
from rich.console import Console
from rich.console import Group
from rich.columns import Columns
from rich.panel import Panel
from rich.prompt import Prompt
from rich.prompt import Confirm
from rich.text import Text
from rich.tree import Tree
from rich.layout import Layout

from acfunsdk import Acer
from acfunsdk import source

__author__ = 'dolacmeo'

terminal_width = 120


def unix2string(t: (int, float, str), f: str = "%Y-%m-%d %H:%M:%S"):
    if len(str(t)) > 10:
        t = int(str(t)[:10])
    return time.strftime(f, time.localtime(t))


def load_image_to_cli(url_or_path, title=None, width=None):
    ansi_rate = 1.3
    is_auto = width is None
    width = min(int(width or 100), terminal_width - 10)  # 最大不超过窗口宽
    _max_height = min(int(width / ansi_rate), console.height - 10)  # 最大高不超出窗口高
    if os.path.isfile(url_or_path):
        _im = Image.open(url_or_path).convert('RGB')
    else:
        _im = Image.open(BytesIO(httpx.get(url_or_path).content)).convert('RGB')
    i_width, i_height = _im.size
    _im = _im.resize((int(i_width * ansi_rate), i_height))  # 拉伸消除变形
    if _im.size[0] != width:  # 定宽 调高
        i_width, i_height = _im.size
        new_h = int(width / i_width * i_height)
        _im = _im.resize((width, new_h), Image.ANTIALIAS)
    if is_auto is True and _im.size[1] > _max_height:  # 超限高调整
        i_width, i_height = _im.size
        new_w = int(_max_height / i_height * i_width)
        _im = _im.resize((new_w, _max_height), Image.ANTIALIAS)
    _ansi = _toAnsi(_im, oWidth=_im.size[0], is_unicode=True, color_type=_color_types.truecolor, palette="default")
    _txt = Text.from_ansi(_ansi)
    return Panel(_txt, subtitle=title, subtitle_align='center', width=_im.size[0] + 4)


console = Console(width=terminal_width)
acer = Acer()

empty_pagelets = ["pagelet_header", "pagelet_banner", "pagelet_spring_festival", "footer"]
contents = {
    "index_title": "[bold #e95c5e]AcFun弹幕视频网 - 认真你就输啦 (・ω・)ノ- ( ゜- ゜)つロ[/bold #e95c5e]",
    "index_ask": "请输入要继续浏览的 [bold red]栏目编号[/bold red]，或者按 [bold red]Q[/bold red] 退出\r\n",
    "index_pagelet": "输入<区块名><空格><编号>来查看内容，多级区块请用 [bold red]-[/bold red] 间隔，"
                     "或者按 [bold red]Q[/bold red] 返回",
    "nav_title": "[bold #e95c5e]导航 - AcFun弹幕视频网[/bold #e95c5e]",
    "nav_ask": "输入<show><空格><编号>可以显示子栏目，输入<open><空格><编号>可以进入栏目，"
               "或者按 [bold red]Q[/bold red] 退出",
    "wen_title": "[bold #e95c5e]文章区 - AcFun弹幕视频网[/bold #e95c5e]",
}


# 个人信息
def acer_info():
    pass


# 个人消息
def acer_message():
    pass


# 首页菜单
def acfun_index_menu():
    acfun_index = acer.AcIndex()
    pagelets = acfun_index.index_pagelets
    pagelet_panels = list()
    pagelets_menu = dict(q=None, Q=None)
    for i, p in enumerate(pagelets):
        if p in empty_pagelets:
            item_name = p[8:] if p.startswith("pagelet_") else p
            item_panel = Panel(f"[black][{i+1}]{source.pagelets_name[p]}[/black]", title=item_name)
        else:
            pagelets_menu[f"{i+1}"] = p
            item_panel = Panel(f"[{i+1}][b]{source.pagelets_name[p]}[/b]", title=f"{p[8:]}")
        pagelet_panels.append(item_panel)
    index_panel = Panel(Columns(pagelet_panels, expand=True, equal=True),
                        title=contents["index_title"], title_align='center',
                        border_style="#e95c5e")
    console.clear()
    console.print(index_panel)
    menu_choice = Prompt.ask(contents["index_ask"], choices=list(pagelets_menu.keys()))
    if pagelets_menu[menu_choice] is None:
        return None
    elif pagelets_menu[menu_choice] == 'pagelet_navigation':
        return 'nav', "1"
    if menu_choice in ['q', "Q"]:
        console.clear()
        sys.exit()
    return acfun_index, pagelets_menu[menu_choice]


# 首页区块
def acfun_index_pagelet(index_obj, area_name: str):
    index_area = index_obj.get(area_name, True)
    lines = list()
    goto = dict()
    # 广告
    if "ad" in index_area:
        ad_name = f"{index_area['ad'].name}"
        ad_url = f"{index_area['ad'].url}"
        if len(ad_name) <= 3:
            ad_text = ad_url
        else:
            ad_text = "\r\n".join([ad_name, ad_url])
        lines.append(Panel(f"{ad_text}", title="ad", title_align='left', border_style='red'))
    # 首页轮播
    if "slider" in index_area:
        slider_data = []
        for n, item in enumerate(index_area['slider']):
            title = f"    {item.name}"
            content = item.url
            if item.container is not None:
                title = f"[{(n+1): >2}] {item.name}"
                content = str(item.container)
            text = Text(style='bold')
            text.append("    " + content)
            text.truncate(terminal_width)
            slider_data.extend([title, text.plain])
        lines.append(Panel("\r\n".join(slider_data), title="slider", title_align='left', border_style='green'))
    # 香蕉榜
    if all(['d1' in index_area, 'd3' in index_area, 'd7' in index_area]):
        for day in ['d1', 'd3', 'd7']:
            day_data = []
            for n, item in enumerate(index_area[day]):
                title = f"[{(n+1): >2}] {str(item)}"
                day_data.append(title)
            lines.append(Panel("\r\n".join(day_data), title=day, title_align='left', border_style='yellow'))

    # 文章区
    if 'article' in index_area:
        pass

    # 频道
    if 'channel' in index_area:
        channel_text = f"{str(index_area['channel'])}"
        lines.append(Panel(channel_text, title="channel", title_align='left', border_style='red'))

    # 链接
    if 'links' in index_area and len(index_area['links']):
        link_data = []
        for n, item in enumerate(index_area['links']):
            if item.__class__.__name__ == 'AcLink':
                title = f"[{(n+1): >2}] {item.name}\r\n{item.url}"
            else:
                title = f"[{(n+1): >2}] {str(item)}"
            link_data.append(title)
        lines.append(Panel("\r\n".join(link_data), title="links", title_align='left', border_style='green'))

    # 内容
    if 'items' in index_area:
        items_data = []
        for n, item in enumerate(index_area['items']):
            goto[f"items_{n+1}"] = item
            title = f"[{(n+1): >2}] {str(item)}"
            items_data.extend([title])
        lines.append(Panel("\r\n".join(items_data), title="items", title_align='left', border_style='cyan'))

    # 排行榜
    if 'rank' in index_area:
        rank_data = []
        for day in ['d1', 'd3', 'd7']:
            day_data = []
            for n, item in enumerate(index_area['rank'][day]):
                title = f"[{(n+1): >2}] {str(item)}"
                day_data.append(title)
            rank_data.append(Panel("\r\n".join(day_data), title=day, title_align='left', border_style='magenta'))
        lines.append(Panel(Group(*rank_data), title="rank", title_align='left', border_style='yellow'))
    index_pagelet = Panel(Group(*lines), title=f"AcFun首页 - {source.pagelets_name[area_name]}", border_style="#e95c5e")

    choice_obj = None
    area, num, where = None, None, None
    while choice_obj is None:
        console.clear()
        console.print(index_pagelet)
        where = Prompt.ask(contents['index_pagelet'])
        if where in ['q', "Q"]:
            return None
        if where.count(" ") > 1:
            where = where.split()
            area, num = where[:2]
        else:
            area = where
        if '-' in area:
            area, sub = area.split()
            datas = index_area.get(area, {}).get(sub)
        else:
            datas = index_area.get(area)
        if datas is None:
            continue
        if isinstance(datas, list) and num.isdigit():
            if num.isdigit():
                num = int(num) - 1
                if num not in range(len(datas)):
                    continue
                choice_obj = datas[num]
            continue
        choice_obj = datas
    if choice_obj.__class__.__name__ == "AcChannel":
        return "nav", choice_obj.cid
    return acfun_detail(choice_obj)


# 频道导航
def acfun_nav(cid: [str, None], block_index: int = -1, mode: str = "nav"):
    cid = "0" if cid in ['', None] else cid
    block_index = -1 if block_index is None else int(block_index)
    if isinstance(block_index, int) and block_index > 0:
        block_index -= 1
    if not cid.isdigit():
        return None
    cid = int(cid)
    navs = acer.nav_data
    title = contents['nav_title']
    nav_id, nav_parent, nav_name = 0, 0, "AcFun栏目"
    if cid != 0 and str(cid) in navs:
        nav_data = navs[str(cid)]
        nav_id = nav_data['id']
        nav_parent = nav_data['parent']
        nav_name = nav_data['navName']
        nav_parent_cid = 0

    main_tree = Tree("AcFun栏目")
    sub_tree = Tree(f"AcFun子栏目")
    for nav in navs.values():
        if nav['id'] == nav_parent:
            nav_parent_cid = nav['cid']
        # 主栏目显示
        if nav['parent'] == 0:
            if nav['cid'] == cid or nav['id'] == nav_parent:
                main_tree.add(f"[bold red][{nav['cid']: >3}] {nav['navName']}[/bold red]")
                sub_tree.__setattr__('label', f"AcFun - [bold red]{nav['navName']}[/bold red]")
            elif nav['cid'] in [177]:  # 频道屏蔽：AC正义
                # main_tree.add(f"[black][{nav['cid']: >3}] {nav['navName']}[/black]")
                continue
            else:
                main_tree.add(f"[{nav['cid']: >3}] {nav['navName']}")
        # 子栏目显示
        if cid != 0 and nav_parent == 0 and nav['parent'] == nav_id:
            sub_tree.add(f"[{nav['cid']: >3}] {nav['navName']}")
        if cid != 0 and nav_parent != 0:
            if nav['cid'] == cid:
                sub_tree.add(f"[bold cyan][{nav['cid']: >3}] {nav['navName']}[/bold cyan]")
            elif nav['parent'] == nav_parent:
                sub_tree.add(f"[{nav['cid']: >3}] {nav['navName']}")

    nav_layout = Layout(name=title)
    nav_layout.split_column(
        Layout(name='nav', size=16),
        Layout(name='block', size=5),
    )
    nav_layout['nav'].split_row(
        Layout(Panel(main_tree), name='main', size=30),
        Layout(Panel(sub_tree, border_style='yellow'), name='sub', size=30),
        Layout(name='ext'),
    )
    realms = None

    if cid == 0 or str(cid) not in navs:
        nav_layout['sub'].visible = False
        nav_layout['ext'].visible = False
    elif cid != 0 and nav_parent == 0:
        ac_channel = acer.AcChannel(cid)
        ac_channel.loading()
        channel_blocks = ac_channel.blocks()
        block_tree = Tree(f"{nav_name}区")
        for i, block in enumerate(channel_blocks):
            if block_index > -1 and i == block_index:
                block_tree.add(f"[cyan][{(i+1): >2}] {str(block)}[/cyan]")
            else:
                block_tree.add(f"[{(i+1): >2}] {str(block)}")
        nav_layout['ext'].update(Panel(block_tree, title=f"{nav_name}区板块", border_style='green'))
    elif cid != 0 and nav_parent != 0:
        ac_channel = acer.AcChannel(cid)
        if ac_channel.parent_data['channelId'] == "63":
            block_tree = Tree(f"文章区 - {nav_name}区")
            channel_realms = list()
            for realm in ac_channel.sub_data['realms']:
                channel_realms.append(realm['realmId'])
                block_tree.add(f"[cyan][{realm['realmId']: >3}][/cyan] {realm['realmName']}")
            realms = ",".join(channel_realms)
            nav_layout['ext'].update(Panel(block_tree, title=f"{nav_name}区 话题", border_style='green'))
        else:
            channel_videos = ac_channel.videos(sortby="rankScore")
            video_list = list()
            for i, video in enumerate(channel_videos[:13]):
                v_num = f"<{(i+1): >2}>"
                v_title = video.video_data.get('title', "")
                v_title = Text(v_title)
                v_title.align('left', 36)
                v_title.truncate(36)
                v_title = v_title.plain
                v_user = video.video_data.get('user', {})
                v_username = v_user.get('name', v_user.get('id', ""))
                v_username = Text(f"@{v_username}")
                v_username.truncate(10)
                v_username = v_username.plain
                v_text = Text(f"{v_num}{v_title} {v_username}")
                video_list.append(v_text.plain)
            video_list.append("... ...")
            nav_layout['ext'].update(Panel("\r\n".join(video_list), border_style='green',
                                           title=f"{nav_name}: [yellow]综合排名[/yellow]"))

    nav_height = 16 + 2
    block_total = 4

    if cid != 0 and (str(cid) in navs) and block_index > -1:
        channel_name = ac_channel.info['name']
        channel_blocks = ac_channel.blocks()
        block_tree = Tree(channel_name)
        for i, block in enumerate(channel_blocks):
            block_tree.add(f"[{(i + 1): >2}] {str(block.name)}")
        choice_block = channel_blocks[block_index]
        content_tree = Tree(f"[{(block_index + 1): >2}] {choice_block.name}")
        block_contents = choice_block.contents()
        block_total += len(block_contents)
        for n, block_content in enumerate(block_contents):
            content_detail = Tree(f"[{(n + 1): >2}] {str(block_content)}")
            content_list = block_content.list()
            block_total += len(content_list)
            for m, ac_obj in enumerate(content_list):
                content_detail.add(f"[{(m + 1): >2}] {ac_obj}")
            content_tree.add(content_detail)
        block_panel_title = f"[{(block_index+1): >2}] {choice_block.name} - {ac_channel.parent_data['name']}"
        block_panel = Panel(content_tree, title=block_panel_title, height=block_total, border_style='magenta')
    else:  # 排行榜
        r_cid, r_sub_cid, limit, d_range = None, None, 10, "DAY"
        rank_ranges = {
            'rank': "DAY",
            'rank1': "DAY",
            'rank3': 'THREE_DAYS',
            'rank7': 'WEEK',
        }
        if mode in rank_ranges:
            d_range = rank_ranges[mode]
        rank_title = f"{d_range}排行榜"
        if cid != 0 and str(cid) in navs:
            if nav_parent == 0:
                r_cid = cid
                rank_title += f" - {nav_name}"
            else:
                r_cid = nav_parent_cid
                r_sub_cid = cid
                rank_title += f" - {navs[str(r_cid)]['navName']}"
                rank_title += f" - {nav_name}"
        ac_rank = acer.AcRank(r_cid, r_sub_cid, limit, d_range)
        rank_tree = Tree(rank_title)
        for n, rank_content in enumerate(ac_rank.contents()):
            block_total += 1
            rank_tree.add(f"[{(n + 1): >2}] {str(rank_content)}")
        block_panel = Panel(rank_tree, height=block_total, border_style='magenta')
    nav_layout['block'].update(block_panel)
    nav_layout['block'].size = block_total
    nav_height += block_total

    nav_panel = Panel(nav_layout, title=contents["nav_title"], title_align='center',
                      border_style="#e95c5e", height=nav_height)

    vs = [None, None, None, None]
    act = None
    while act not in ['open', 'show', 'q', "Q"]:
        console.clear()
        console.print(nav_panel)
        nav_act = Prompt.ask(contents['nav_ask'])
        if nav_act in ['q', "Q"]:
            console.clear()
            sys.exit()
        elif nav_act.count(" ") < 1:
            continue
        for i, x in enumerate(nav_act.split()):
            vs[i] = x
        act, act_cid, block_i, item_index = vs
        if act not in ['open', 'show']:
            continue
        if act == 'show':
            return mode, act_cid, block_i
        elif act == 'open':
            # 文章区
            if act_cid in list(map(str, [63, 184, 110, 73, 164, 74, 75])):
                return 'wen', realms
            result = acfun_video(act_cid)
            if result is None:
                continue
            return result
        elif act == 'back':
            return 'back'
    pass


def acfun_video(cid, sortby: [str, None] = None):
    ac_video = acer.AcChannel(cid)
    ac_video.video_data = list()

    def build_panel(page: int):
        is_feed = False
        if page > len(ac_video.video_data):
            is_feed = True
            feed_data = ac_video.videos(page, sortby=sortby, obj=False)
            ac_video.video_data.extend([feed_data[:10], feed_data[10:20], feed_data[20:]])
        now_total = len(ac_video.video_data)
        feed_list = list()
        for i, v in enumerate(ac_video.video_data[page - 1]):
            pick_num = 0 if (i + 1) > 9 else i + 1
            username = v['user']['name']
            v_text = f"[cyan][{pick_num}][/cyan] [b][ac{v['ac_num']}]{v['title']}[/b]\r\n" \
                     f"[#333333][{v['duration']}][/#333333] " \
                     f"👀{v['viewCountShow']} 💬{v['commentCountShow']} " \
                     f"[yellow]@{username}[/yellow]"
            feed_list.append(v_text)
        this_title = f"{'最新' if is_feed else '回看'} 第{page}页"
        if is_feed is False:
            this_title += f"/总{now_total}页"
        return Panel(Panel("\r\n".join(feed_list), title=this_title, title_align='left', height=22),
                     title=contents["index_title"], title_align='center', border_style="#e95c5e")
    now_page = 1
    ac_video_panel = build_panel(now_page)
    now_exit = False
    while now_exit is False:
        console.clear()
        console.print(ac_video_panel)
        event = keyboard.read_event()
        if event.event_type == keyboard.KEY_DOWN:
            # console.print(event.name)
            if event.name == 'right':
                now_page += 1
                ac_video_panel = build_panel(now_page)
            elif event.name == 'left' and now_page > 1:
                now_page -= 1
                ac_video_panel = build_panel(now_page)
            elif event.name == 'up':
                now_page = 1
                ac_video_panel = build_panel(now_page)
            elif event.name == 'down':
                now_page = len(ac_video.video_data)
                ac_video_panel = build_panel(now_page)
            elif event.name == 'esc':
                now_exit = True
                console.clear()
            elif event.name in list(map(str, range(10))):
                now_exit = True
                console.clear()
            elif event.name in ['backspace', 'delete']:
                return 'back'
            elif event.name == 'ctrl':
                acfun_cmd = Prompt.ask("acfun ").split()
                return acfun_cmd
    return None


# 文章区
def acfun_wen(realms=None, sortType: [str, None] = None):
    sortType = "createTime" if sortType is None else sortType
    ac_wen = acer.AcWen(realms, sortType)
    status_panel = f""

    def get_feed(page: int):
        is_feed = True
        now_total = len(ac_wen.article_data) // 10
        if now_total < 1:
            feed_wen = ac_wen.feed(False)
        elif page > now_total:
            feed_wen = ac_wen.feed(False)
        elif page <= now_total:
            is_feed = False
            feed_wen = ac_wen.article_data[((page - 1) * 10): (page * 10)]
        else:
            feed_wen = ac_wen.feed(False)
        feed_list = list()
        for i, wen in enumerate(feed_wen):
            pick_num = 0 if (i + 1) > 9 else i + 1
            title = wen['title']
            ac_num = wen['articleId']
            username = wen['userName']
            wen_text = f"[cyan][{pick_num}][/cyan] [b][ac{ac_num}]{title}[/b]\r\n" \
                       f"    [#999999][{wen['realmName']}][/#999999] " \
                       f"[#333333][{unix2string(wen['createTime'])}][/#333333] " \
                       f"👀{wen['viewCount']} 💬{wen['commentCount']} " \
                       f"[yellow]@{username}[/yellow]"
            feed_list.append(wen_text)
        this_title = f"{'最新' if is_feed else '回看'} 第{page}页"
        if is_feed is False:
            this_title += f"/总{now_total}页"
        return Panel(Panel("\r\n".join(feed_list), title=this_title, title_align='left', height=22),
                     title=contents["index_title"], title_align='center', border_style="#e95c5e")
    now_page = 1
    ac_wen_panel = get_feed(now_page)
    now_exit = False
    while now_exit is False:
        console.clear()
        console.print(ac_wen_panel)
        event = keyboard.read_event()
        if event.event_type == keyboard.KEY_DOWN:
            # console.print(event.name)
            if event.name == 'right':
                now_page += 1
                ac_wen_panel = get_feed(now_page)
            elif event.name == 'left' and now_page > 1:
                now_page -= 1
                ac_wen_panel = get_feed(now_page)
            elif event.name == 'up':
                now_page = 1
                ac_wen_panel = get_feed(now_page)
            elif event.name == 'down':
                now_page = len(ac_wen.article_data) // 10
                ac_wen_panel = get_feed(now_page)
            elif event.name == 'esc':
                now_exit = True
                console.clear()
            elif event.name in list(map(str, range(10))):
                now_exit = True
                console.clear()
            elif event.name in ['backspace', 'delete']:
                return 'back'
            elif event.name == 'ctrl':
                acfun_cmd = Prompt.ask("acfun ").split()
                return acfun_cmd
    return None


# 显示图片
def acfun_image(url, title=None, width=None):
    img_panel = load_image_to_cli(url, title, width)
    console.print(img_panel)
    console.print('图片已显示，点击空格继续...')
    keyboard.wait('space')
    return None


# 详情菜单
def acfun_detail(ac_obj, act=None, ext=None):
    if ac_obj is None:
        return None
    obj_type = ac_obj.__class__.__name__
    if obj_type == "AcImage":
        return acfun_image(ac_obj.src, act, ext)
    elif obj_type == 'AcLink':
        console.print("未知链接:", ac_obj.url)
    elif obj_type == 'AcChannel':
        return "nav", ac_obj.cid, None, None
    elif obj_type == 'AcArticle':
        pass
    elif obj_type == 'AcVideo':
        pass
    elif obj_type == 'AcBangumi':
        pass
    elif obj_type == 'AcAlbum':
        pass
    elif obj_type == 'AcUp':
        up_layout = Layout()
        up_layout.split_row(
            Layout(name='info', size=92),
            Layout(name='avatar', size=24),
        )
        ac_obj.loading()
        up_uid = ac_obj.up_data['userId']
        up_name = ac_obj.up_data['name']
        up_avatar = ac_obj.up_data['headUrl']
        signature = ac_obj.up_data['signature'].strip() or ""
        signature = signature.replace('\n', '↩ ')
        reg_time = unix2string(ac_obj.up_data['registerTime'])
        login_time = unix2string(ac_obj.up_data['lastLoginTime'])
        info_text = f"UID: {up_uid} \r\n" \
                    f"昵称: {up_name} \r\n" \
                    f"签名: {signature} \r\n" \
                    f"注册时间: {reg_time} \r\n" \
                    f"最后登录: {login_time} \r\n" \
                    f"关注: {ac_obj.following_count: >4} | 粉丝: {ac_obj.followed_count} \r\n" \
                    f"视频: {ac_obj.video_count: >4} | 文章: {ac_obj.article_count: >4} " \
                    f"| 合集: {ac_obj.album_count: >2}"
        up_layout['info'].update(Panel(info_text, title=up_name))
        up_avatar = load_image_to_cli(up_avatar, f"{up_uid}", 20)
        up_avatar.height = 9
        up_layout['avatar'].update(up_avatar)
        console.print(Panel(up_layout, height=11))
    return None


# 评论区
def acfun_comment():
    pass


# 直播弹幕
def acfun_live_danmaku():
    pass


@click.command()
@click.argument('src', default='help')
@click.argument('act', default="", nargs=1)
@click.option('--ext')
@click.option('--login')
def cli(src, act=None, ext=None, login=None):
    act = None if act == "" else act
    ext = None if ext == "" else ext
    history = [[src, act, ext, login]]
    while True:
        if src == 'help':
            click.echo(f"Need Help?")
        elif src.startswith('http') and parse.urlsplit(src).netloc.endswith('acfun.cn'):
            result = acfun_detail(acer.get(src), act=act, ext=ext)
            if result is None:
                break
            src, act, ext, login = result
        elif src in ['index', 'nav', 'rank', 'rank1', 'rank3', 'rank7', 'wen', 'signin']:
            click.echo(f"{src}: {act}")
            if src == 'index':
                result = acfun_index_menu()
                if result is None:
                    break
                if result[0] in ['index', 'nav']:
                    src, act = result
                    continue
                result = acfun_index_pagelet(*result)
                if result[0] in ['index', 'nav']:
                    src, act = result
                    continue
                if result is None:
                    continue
            elif src in ['nav', 'rank', 'rank1', 'rank3', 'rank7']:
                result = acfun_nav(act, ext, src)
                if isinstance(result, tuple):
                    if len(result) == 2:
                        src, act = result
                    elif len(result) == 3:
                        src, act, ext = result
                elif result is None:
                    break
            elif src in ['wen']:
                if isinstance(act, str) and act.count(','):
                    act = act.split(',')
                result = acfun_wen(act, ext)
                if isinstance(result, (tuple, list)):
                    if len(result) == 1:
                        src, act = result[0], None
                    elif len(result) == 2:
                        src, act = result
                    elif len(result) == 3:
                        src, act, ext = result
                elif result is None:
                    break

        if src == 'back':
            if len(history) > 2:
                history = history[:-1]
                src, act, ext, login = history[-1]
            else:
                break
        elif [src, act, ext, login] != history[-1]:
            history.append([src, act, ext, login])
    pass


if __name__ == '__main__':
    cli()
