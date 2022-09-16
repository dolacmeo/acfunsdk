# coding=utf-8
import os
import re
import time
import click
import httpx
import subprocess
from html import unescape
from datetime import timedelta
from acfunsdk.libs.climage import _toAnsi
from acfunsdk.libs.climage import _color_types
from io import BytesIO
from PIL import Image
from urllib import parse
from rich.console import Console
from rich.console import Group
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text
from rich.layout import Layout
from rich.live import Live
from rich.align import Align
import emoji

from acfunsdk import Acer
from acfunsdk import source

__author__ = 'dolacmeo'

terminal_width = 120


def unix2string(t: (int, float, str), f: str = "%Y-%m-%d %H:%M:%S"):
    if len(str(t)) > 10:
        t = int(str(t)[:10])
    return time.strftime(f, time.localtime(t))


def load_image_to_cli(url_or_path, title=None, width=None, title_align=None):
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
    _ansi = _toAnsi(_im, oWidth=_im.size[0], is_unicode=True,
                    color_type=_color_types.truecolor, palette="default")
    _txt = Text.from_ansi(_ansi)
    return Panel(_txt, subtitle=title, subtitle_align=title_align or 'center', width=_im.size[0] + 4)


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
    "404": "[red]【404】咦？世界线变动了，你好像来到了奇怪的地方。看看其他内容吧~[/red]"
}


def cli_image(ac_obj, title=None, width=None):
    img_panel = load_image_to_cli(ac_obj.src, title, width)
    console.clear()
    console.print(img_panel)
    return None


def cli_video(ac_obj, act=None, ext=None):
    cmd_log = []
    video_layout = Layout()
    video_layout.split_column(
        Layout(name='title', size=2),
        Layout(name='info', size=28)
    )
    video_layout['title'].split_row(
        Layout(name='title-main', size=87),
        Layout(name='title-sub', size=28),
    )
    video_layout['info'].split_row(
        Layout(name='video', size=88),
        Layout(name='acup', size=28),
    )
    video_layout['video'].split_column(
        Layout(name='cover_img', size=20),
        Layout(name='base_info', size=8)
    )
    video_layout['acup'].split_column(
        Layout(name='avatar', size=10),
        Layout(name='upinfo')
    )
    video_raw = ac_obj.video_data
    video_title = video_raw['title'].strip()
    video_title = video_title.replace("️", "")
    title_text = f" [b]{video_title}[/b]\r\n" \
                 f" {video_raw['channel']['parentName']} > {video_raw['channel']['name']}    " \
                 f"👀{video_raw['viewCount']}  🔗{video_raw['shareCount']}  " \
                 f"评{video_raw['commentCount']}  弹{video_raw['danmakuCount']}"
    video_layout['title-main'].update(title_text)
    video_create = unix2string(video_raw['createTimeMillis'])
    subtitle_text = f"⏰[{video_create}]\r\n" \
                    f"👍{video_raw['likeCount']}  🌟{video_raw['stowCount']}  🍌{video_raw['bananaCount']}"
    subtitle = Text(subtitle_text, justify='right')
    video_layout['title-sub'].update(subtitle)

    video_duration = str(timedelta(milliseconds=video_raw['durationMillis']))
    video_duration = video_duration.split('.')[0]
    if video_duration.startswith('0:'):
        video_duration = video_duration[3:]
    cover_title = f"▶ 0:00/{video_duration}"
    cover_panel = load_image_to_cli(video_raw['coverUrl'], title=cover_title, width=84, title_align='left')
    cover_panel.title = f"[#62a5ff]{source.routes['video']}{ac_obj.ac_num}[/#62a5ff]"
    cover_panel.title_align = 'left'
    video_layout['cover_img'].update(cover_panel)
    acup = video_raw['user']
    avatar_panel = load_image_to_cli(acup['headUrl'], acup['name'], 24)
    if acup.get('verifiedText'):
        avatar_panel.title = acup['verifiedText']
    video_layout['avatar'].update(avatar_panel)

    up_text = f"| 关  注 | 粉  丝 | 投  稿 |\r\n" \
              f"| {acup['followingCount']: >6} | " \
              f"{acup['fanCount']: >6} | " \
              f"{acup['contributeCount']: >6} |"
    up_stat = Text(up_text)
    video_staff = ac_obj.staff()
    if video_staff is None:
        signature = acup['signature'].replace('\n', '↩').replace('\r', '')
        signature = unescape(signature)
        signature = Panel(emoji.replace_emoji(signature, ""), title='签名', title_align='left', height=16)
        video_layout['upinfo'].update(Group(up_stat, signature))
    else:
        staff_text = [
            f"{video_staff['upInfo']['staffRoleName']}:{video_staff['upInfo']['name']}"
        ]
        for up in video_staff['staffInfos']:
            staff_text.append(f"{up['staffRoleName']}:{up['name']}")
        staff_panel = Panel("\r\n".join(staff_text), title='联合出品', title_align='left', height=16)
        video_layout['upinfo'].update(Group(up_stat, staff_panel))

    video_info = f"{video_raw['description'] or '暂无简介'}\r\n"
    ac_link_rex = r"(\[a[ac]=\d*@(video|album|article)\]([^\[]*)\[\/a[ac]\])"
    if video_raw['description']:
        info_link = re.compile(ac_link_rex).findall(video_info)
        for link in info_link:
            video_info = video_info.replace(link[0], f"[#62a5ff]{link[2]}[/#62a5ff] ")

    video_tags = " ".join([f"[{x['name']}]" for x in video_raw.get('tagList', [])])
    info_panel = Panel(video_info, subtitle=video_tags, subtitle_align='left')
    if 'originalDeclare' in video_raw:
        info_panel.title = "🚫未经作者授权，禁止转载"
        info_panel.title_align = 'right'
    video_layout['base_info'].update(info_panel)

    video_title = "[bold #e95c5e]AcFun弹幕视频网 - " \
                 "认真你就输啦 (・ω・)ノ- ( ゜- ゜)つロ[/bold #e95c5e]"
    video_panel = Panel(video_layout, height=32, title=video_title, title_align='center', border_style="#e95c5e")

    console.clear()
    console.print(video_panel)
    # 功能按钮：弹幕、评论、UP
    return None


def cli_bangumi(ac_obj, act=None, ext=None):
    bangumi_layout = Layout()
    bangumi_layout.split_column(
        Layout(name='title', size=2),
        Layout(name='info', size=28)
    )
    bangumi_layout['title'].split_row(
        Layout(name='title-main', size=87),
        Layout(name='title-sub', size=28),
    )
    bangumi_layout['info'].split_row(
        Layout(name='cover', size=56),
        Layout(name='detail', size=60),
    )
    bangumi_layout['detail'].split_column(
        Layout(name='season', size=3),
        Layout(name='episode'),
    )
    bangumi_raw = ac_obj.bangumi_data
    bangumi_title = bangumi_raw['bangumiTitle'].strip()
    bangumi_text = f" [ {bangumi_raw['extendsStatus']} ] [b]{bangumi_title}[/b]\r\n" \
                   f" [ {bangumi_raw['bangumiPaymentType']['name']} ] " \
                   f"看{bangumi_raw['playCountShow']}  " \
                   f"评{bangumi_raw['commentCountShow']}"
    bangumi_layout['title-main'].update(bangumi_text)
    subtitle_text = f"⏰[{bangumi_raw['updateTime']}]\r\n" \
                    f"👍{bangumi_raw['bangumiLikeCountShow']}  " \
                    f"🌟{bangumi_raw['stowCountShow']}  " \
                    f"🍌{bangumi_raw['bangumiBananaCountShow']}"
    subtitle = Text(subtitle_text, justify='right')
    bangumi_layout['title-sub'].update(subtitle)
    cover_panel = load_image_to_cli(bangumi_raw['bangumiCoverImageV'], width=52)
    cover_panel.title = f"[#62a5ff]{source.routes['video']}{ac_obj.aa_num}[/#62a5ff]"
    cover_panel.title_align = 'left'
    bangumi_layout['cover'].update(cover_panel)
    if len(bangumi_raw['relatedBangumis']) == 0:
        bangumi_layout['season'].visible = False
    else:
        season_list = []
        for x in bangumi_raw['relatedBangumis']:
            season_list.append(f"{x['name']}")
        season_txt = Text(" | ".join(season_list), style='bold')
        season_txt.align('center', 56)
        season_panel = Panel(season_txt, title="更多季", title_align='right')
        bangumi_layout['season'].update(season_panel)

    intro_text = [
        f"{bangumi_title} {bangumi_raw['latestItem']} {bangumi_raw['extendsStatus']}",
        bangumi_raw['bangumiIntro']
    ]
    intro_panel = Panel("\r\n".join(intro_text), title="番剧简介", title_align='left')
    bangumi_layout['episode'].update(intro_panel)

    bangumi_title = "[bold #e95c5e]AcFun弹幕视频网 - " \
                    "认真你就输啦 (・ω・)ノ- ( ゜- ゜)つロ[/bold #e95c5e]"
    bangumi_panel = Panel(bangumi_layout, height=32, title=bangumi_title, title_align='center', border_style="#e95c5e")

    console.clear()
    console.print(bangumi_panel)
    # 功能按钮：弹幕、评论
    return None


def cli_article(ac_obj, act=None, ext=None):
    # 分类 标题         用户图
    # 时间、状态        用户信息
    # 简介
    # 功能按钮：正文、评论
    return None


def cli_acup(ac_obj, act=None, ext=None):
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
    up_title = f"@{up_name}"
    if ac_obj.up_data['isContractUp']:
        up_title = f"[red]{up_title}[/red]"
    if ac_obj.up_data.get('verifiedText'):
        up_title = f"[b]{up_title}[/b] | {ac_obj.up_data['verifiedText']}"
    info_subtitle = f"注册时间: {reg_time} | 最后登录: {login_time}"
    detail_text = f"关注: {ac_obj.following_count: >6} | " \
                  f"粉丝: {ac_obj.followed_count: >6} | " \
                  f"视频: {ac_obj.video_count: >6} | " \
                  f"文章: {ac_obj.article_count: >6} | " \
                  f"合集: {ac_obj.album_count: >6} \r\n" \
                  f"{signature}"
    info_panel = Panel(detail_text, title=up_title, title_align='left',
                       subtitle=info_subtitle)
    up_layout['info'].update(info_panel)
    up_avatar = load_image_to_cli(up_avatar, width=20)
    up_avatar.title = f"UID:{up_uid}"
    up_avatar.height = 9
    if len(ac_obj.up_data['verifiedTypes']):
        verifed_icon = []
        for x in ac_obj.up_data['verifiedTypes']:
            if x == 1:  # AcFun管理员
                verifed_icon.append("🐒")
            elif x == 2:  # AcFun官方认证
                verifed_icon.append("✅")
            elif x == 3:  # AVI虚拟偶像标识
                verifed_icon.append("✨")
            elif x == 4:  # 高弹达人标识???
                verifed_icon.append("🏆")
            elif x == 5:  # 阿普学院标志
                verifed_icon.append("🎓")
        up_avatar.subtitle = " ".join(verifed_icon)
    up_layout['avatar'].update(up_avatar)
    up_panel = Panel(up_layout, height=11, border_style="#e95c5e")


    console.clear()
    console.print(up_panel)
    return None


def cli_live(ac_obj, act=None, ext=None):
    ac_obj.media_list()
    if ac_obj.is_open is False:
        console.print("[bold red]直播已关播[/bold red]")
        return None
    is_out = False
    login_string = ""
    cmd_log = []

    def live_panel():
        live_layout = Layout()
        live_layout.split_column(
            Layout(name='title', size=2),
            Layout(name='info', size=20),
            Layout(name='bottom', size=9)
        )
        live_layout['title'].split_row(
            Layout(name='title-main', size=87),
            Layout(name='title-sub', size=28),
        )
        live_layout['info'].split_row(
            Layout(name='cover', size=88),
            Layout(name='acup', size=28),
        )
        live_layout['acup'].split_column(
            Layout(name='avatar', size=10),
            Layout(name='upinfo')
        )
        live_layout['bottom'].split_row(
            Layout(name='tips', size=88),
            Layout(name='log', size=28)
        )
        live_raw = ac_obj.infos()
        title_text = f" [{live_raw['href']}][b]{live_raw['title']}[/b]\r\n" \
                     f" 直播 > {live_raw['type']['categoryName']} > {live_raw['type']['name']}"
        live_layout['title-main'].update(title_text)
        live_start = unix2string(live_raw['createTime'])
        subtitle_text = f"👤{live_raw['onlineCount']}  💖{live_raw['likeCount']}  \r\n" \
                        f"⏰[{live_start}]"
        subtitle = Text(subtitle_text, justify='right')
        live_layout['title-sub'].update(subtitle)
        cover_url = live_raw['coverUrls'][0]
        cover_panel = load_image_to_cli(cover_url, width=84)
        live_layout['cover'].update(cover_panel)
        acup = live_raw['user']
        avatar_panel = load_image_to_cli(acup['headUrl'], acup['name'], 24)
        if 'verifiedText' in acup:
            avatar_panel.title = acup['verifiedText']
        live_layout['avatar'].update(avatar_panel)
        up_text = f"| 关  注 | 粉  丝 | 投  稿 |\r\n" \
                  f"| {acup['followingCount']: >6} |" \
                  f"{acup['fanCount']: >6} | " \
                  f"{acup['contributeCount']: >6} |"
        up_stat = Text(up_text)
        signature = acup['signature'].replace('\n', '↩').replace('\r', '')
        signature = Panel(emoji.replace_emoji(signature, ""), title='签名', title_align='left', height=8)
        live_layout['upinfo'].update(Group(up_stat, signature))
        action_text = [
            f" 1.看弹幕(danmaku PotPlayer路径)，会弹出新窗口播放弹幕，播放器可选",
            f" 2.录制(record 保存目录路径)，会弹出新窗口，保存目录可选，默认当前",
            f" 3.给主播点赞(like 次数)，每个赞1秒，别弄太多哦",
            f" 4.登录后发弹幕(push 内容)，发完可以到弹幕窗口查看",
            f" 5.登录后送礼物(gift 编号 数量 次数)，礼物编号什么的没法告诉你，反正 1 是香蕉",
            f" 6.登录(login 用户名:密码)，已登录可用(login 用户名)",
            f" 7.退出(quit)，那就下次再见! [阿妹你看 上帝压狗]"
        ]
        tip_panel = Panel("\r\n".join(action_text), title="操作命令", title_align='left', height=9)
        if acer.is_logined:
            action_text[3] = action_text[3].replace('登录后', "")
            action_text[4] = action_text[4].replace('登录后', "")
            action_text[5] = f" 5.退出登录(logout)"
            tip_panel = Panel("\r\n".join(action_text), title="操作命令", title_align='left', height=9)
        live_layout['tips'].update(tip_panel)
        live_title = "[bold #e95c5e]直播 - AcFun弹幕视频网 - " \
                     "认真你就输啦 (・ω・)ノ- ( ゜- ゜)つロ[/bold #e95c5e]"
        live_log = "\r\n".join(cmd_log)
        live_layout['log'].update(Panel(live_log, title='命令日志', title_align='right'))
        return Panel(live_layout, height=33, title=live_title, title_align='center', border_style="#e95c5e")

    console.clear()
    with Live(console=console, auto_refresh=False) as live:
        while is_out is False and ac_obj.media_list() is not False:
            live.console.clear()
            live.update(live_panel(), refresh=True)
            user_cmd = Prompt.ask("命令").strip()
            if len(user_cmd) == 0:
                continue
            if user_cmd.lower() == 'quit':
                is_out = True
                continue
            elif user_cmd.lower() == 'logout':
                global acer
                acer = Acer()
                cmd_log.append("logout")
                continue
            elif user_cmd.lower() == 'like':
                ac_obj.like(1)
                cmd_log.append("like")
                continue
            elif user_cmd.lower() == 'record':
                cmds = [
                    "start", "cmd", "/q", "/c",
                    f"chcp 65001 && mode con cols=52 lines=4 && title AcLive({ac_obj.uid}) &&",
                    "acfun", f"{source.routes['live']}{ac_obj.uid}", "record"
                ]
                subprocess.Popen(cmds, shell=True)
                cmd_log.append("record[only]")
                continue
            elif user_cmd.lower() == 'danmaku':
                cmds = [
                    "start", "cmd", "/q", "/c",
                    f"chcp 65001 && mode con cols=80 lines=60 && title AcLive({ac_obj.uid}) &&",
                    "acfun", f"{source.routes['live']}{ac_obj.uid}", "danmaku"
                ]
                if login_string:
                    cmds += ["--login", login_string]
                subprocess.Popen(cmds, shell=True)
                cmd_log.append("danmaku[only]")
                continue
            user_cmd = user_cmd.split(maxsplit=1)
            if len(user_cmd) == 2 and user_cmd[0] == 'login':
                if user_cmd[1].count(":") == 1:
                    name, pwd = user_cmd[1].split(":")
                    acer.login(name, pwd)
                    login_string = user_cmd[1]
                    continue
                if (len(user_cmd[1]) == 11 and user_cmd[1].isdigit()) or user_cmd[1].count("@") == 1:
                    if os.path.isfile(f"{user_cmd[1]}.cookies"):
                        acer.loading(user_cmd[1])
                        login_string = user_cmd[1]
                        continue
                cmd_log.append("login")
            elif len(user_cmd) == 2 and user_cmd[0] == 'danmaku':
                if user_cmd[1][0] == user_cmd[1][-1] and user_cmd[1][0] in ["'", '"']:
                    user_cmd[1] = user_cmd[1][1:-1]
                cmds = [
                    "start", "cmd", "/q", "/c",
                    f"chcp 65001 && mode con cols=80 lines=60 && title AcLive({ac_obj.uid}) &&",
                    "acfun", f"{source.routes['live']}{ac_obj.uid}", "danmaku",
                    "--ext", f"{user_cmd[1]}"
                ]
                if login_string:
                    cmds += ["--login", login_string]
                subprocess.Popen(cmds, shell=True)
                cmd_log.append("danmaku[player]")
                continue
            elif len(user_cmd) == 2 and user_cmd[0] == 'record':
                if user_cmd[1][0] == user_cmd[1][-1] and user_cmd[1][0] in ["'", '"']:
                    user_cmd[1] = user_cmd[1][1:-1]
                cmds = [
                    "start", "cmd", "/q", "/c",
                    f"chcp 65001 && mode con cols=52 lines=4 && title AcLive({ac_obj.uid}) &&",
                    "acfun", f"{source.routes['live']}{ac_obj.uid}", "record",
                    "--ext", f"{user_cmd[1]}"
                ]
                if login_string:
                    cmds += ["--login", login_string]
                subprocess.Popen(cmds, shell=True)
                cmd_log.append("record[with path]")
                continue
            elif user_cmd[0] == 'like' and user_cmd[1].isdigit():
                if int(user_cmd[1]) <= 600:
                    cmds = [
                        "start", "cmd", "/c",
                        f"chcp 65001 && mode con cols=52 lines=4 && title AcLive({ac_obj.uid}) &&",
                        "acfun", f"{source.routes['live']}{ac_obj.uid}", "like",
                        "--ext", f"{user_cmd[1]}",
                        "--login", login_string
                    ]
                    subprocess.Popen(cmds, shell=True)
                    cmd_log.append(" ".join(user_cmd))
            elif user_cmd[0] == 'push':
                if acer.is_logined:
                    ac_obj.push_danmaku(user_cmd[1])
                    cmd_log.append("push")
                else:
                    console.print("need login!")
    console.clear()
    return None


# 详情菜单
def acfun_detail(ac_obj, act=None, ext=None):
    if ac_obj is None:
        return None
    if ac_obj.is_404:
        console.print(contents['404'])
        return None
    obj_type = ac_obj.__class__.__name__
    if obj_type in ['AcLink', 'AcChannel', 'AcAlbum']:
        pass
    elif obj_type == "AcImage":
        return cli_image(ac_obj, act, ext)
    elif obj_type == 'AcVideo':
        return cli_video(ac_obj, act, ext)
    elif obj_type == 'AcBangumi':
        return cli_bangumi(ac_obj, act, ext)
    elif obj_type == 'AcArticle':
        pass
    elif obj_type == 'AcUp':
        return cli_acup(ac_obj, act, ext)
    elif obj_type == "AcLiveUp":
        if act == 'danmaku':
            console.print(f"直播弹幕暂不可用")
            # ac_obj.watching_danmaku(potplayer=ext)
            return None
        elif act == 'record':
            save_path = os.getcwd() if ext is None else ext
            ac_obj.record(save_path)
            return None
        elif act == 'like':
            if isinstance(ext, str) and ext.isdigit():
                console.print(f"正在执行点赞{ext}个\r\n完成后窗口自动关闭")
                ac_obj.like(int(ext) or 1)
            return None
        return cli_live(ac_obj, act, ext)
    console.print(f"抱歉，暂不支持命令行预览 {obj_type} 类型")
    return None


@click.command()
@click.argument('src', default='help')
@click.argument('act', default="", nargs=1)
@click.option('--ext')
@click.option('--login', help="username:password or username")
def cli(src, act=None, ext=None, login=None):
    act = None if act == "" else act
    ext = None if ext == "" else ext
    login = None if login == "" else login
    if isinstance(login, str):
        if login.count(":") == 1:
            username, password = login.split(':')
            acer.login(username, password)
        if (len(login) == 11 and login.isdigit()) or login.count("@") == 1:
            if os.path.isfile(f"{login}.cookies"):
                acer.loading(login)
    while True:
        if src == 'help':  # 帮助
            help_words = """
1. login(first time)
    [cyan]acfun[/cyan] ... [i]--login[/i] <username:password>
   login(use cookie)
    [cyan]acfun[/cyan] ... [i]--login[/i] <username>
2. Preview page
    [cyan]acfun[/cyan] <url>
3. Preview page with num
    [cyan]acfun[/cyan] [yellow]up[/yellow] <num>
    [cyan]acfun[/cyan] [yellow]live[/yellow] <num>
    [cyan]acfun[/cyan] [yellow]video[/yellow] <num>
    [cyan]acfun[/cyan] [yellow]bangumi[/yellow] <num>
4. Signin with login
    [cyan]acfun[/cyan] [yellow]signin[/yellow] [i]--login[/i] <username:password>
5. LiveDanmaku in CMD
    [cyan]acfun[/cyan] <live_url> [yellow]danmaku[/yellow]
6. LiveDanmaku in CMD and open player
    [cyan]acfun[/cyan] <live_url> [yellow]danmaku[/yellow] [i]--ext[/i] <player_path>
"""
            console.clear()
            console.print(Panel(help_words, title="ACFUNSDK CLI"))
            return None
        elif src == 'signin':  # 签到
            acer.signin()
            return None
        elif src.startswith('http') and parse.urlsplit(src).netloc.endswith('acfun.cn'):
            return acfun_detail(acer.get(src), act=act, ext=ext)
        elif src.lower() in ['video', 'bangumi', 'live', 'up']:
            if src.lower() == 'video':
                return cli_video(acer.AcVideo(act))
            elif src.lower() == 'bangumi':
                return cli_video(acer.AcBangumi(act))
            elif src.lower() == 'live':
                return cli_video(acer.AcLiveUp(act))
            elif src.lower() == 'up':
                return cli_video(acer.AcUp(dict(userId=act)))
            return None

    pass


if __name__ == '__main__':
    cli()
