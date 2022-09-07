# coding=utf-8
import os
import re
import sys
import time
import click
import httpx
import keyboard
import subprocess
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
import emoji

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
    _ansi = _toAnsi(_im, oWidth=_im.size[0], is_unicode=True,
                    color_type=_color_types.truecolor, palette="default")
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


def cli_image(ac_obj, title=None, width=None):
    img_panel = load_image_to_cli(ac_obj.src, title, width)
    console.print(img_panel)
    console.print('图片已显示，点击空格继续...')
    keyboard.wait('space')
    return None


def cli_video(ac_obj, act=None, ext=None):
    # 封面图    用户图
    #           用户信息
    # 视频信息
    # 功能按钮：弹幕、评论、UP
    pass


def cli_bangumi(ac_obj, act=None, ext=None):
    # 封面图    分集列表
    #           分集列表
    # 视频信息  分集列表
    # 功能按钮：弹幕、评论
    pass


def cli_article(ac_obj, act=None, ext=None):
    # 分类 标题         用户图
    # 时间、状态        用户信息
    # 简介
    # 功能按钮：正文、评论
    pass


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
    pass


def cli_live(ac_obj, act=None, ext=None):
    is_out = False
    cmd_log = []

    def live_panel():
        live_layout = Layout()
        live_layout.split_column(
            Layout(name='title', size=2),
            Layout(name='info', size=20),
            Layout(name='bottom', size=8)
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
        if acup['verifiedText']:
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
            f" 2.给主播点赞(like 次数)，每个赞1秒，别弄太多哦",
            f" 3.登录后发弹幕(push 内容)，发完可以到弹幕窗口查看",
            f" 4.登录后送礼物(gift 编号 数量 次数)，礼物编号什么的没法告诉你，反正 1 是香蕉",
            f" 5.登录(login 用户名:密码)，已登录可用(login 用户名)",
            f" 6.退出(quit)，那就下次再见! [阿妹你看 上帝压狗]"
        ]
        tip_panel = Panel("\r\n".join(action_text), title="操作命令", title_align='left', height=8)
        if acer.is_logined:
            action_text[2] = action_text[2].replace('登录后', "")
            action_text[3] = action_text[3].replace('登录后', "")
            action_text[4] = f" 5.退出登录(logout)"
            tip_panel = Panel("\r\n".join(action_text), title="操作命令", title_align='left', height=8)
        live_layout['tips'].update(tip_panel)
        live_title = "[bold #e95c5e]直播 - AcFun弹幕视频网 - " \
                     "认真你就输啦 (・ω・)ノ- ( ゜- ゜)つロ[/bold #e95c5e]"
        live_log = "\r\n".join(cmd_log)
        live_layout['log'].update(Panel(live_log, title='命令日志', title_align='right'))
        return Panel(live_layout, height=32, title=live_title, title_align='center')

    while is_out is False:
        console.clear()
        console.print(live_panel())
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
        elif user_cmd.lower() == 'danmaku':
            os.system(f"start cmd /c acfun {source.routes['live']}{ac_obj.uid} danmaku")
            cmd_log.append("danmaku")
            continue
        user_cmd = user_cmd.split(maxsplit=1)
        if len(user_cmd) == 2 and user_cmd[0] == 'login':
            if user_cmd[1].count(":") == 1:
                name, pwd = user_cmd[1].split(":")
                acer.login(name, pwd)
                continue
            if (len(user_cmd[1]) == 11 and user_cmd[1].isdigit()) or user_cmd[1].count("@") == 1:
                if os.path.isfile(f"{user_cmd[1]}.cookies"):
                    acer.loading(user_cmd[1])
                    continue
            cmd_log.append("login")
        elif len(user_cmd) == 2 and user_cmd[0] == 'danmaku':
            if user_cmd[1][0] == user_cmd[1][-1] and user_cmd[1][0] in ["'", '"']:
                user_cmd[1] = user_cmd[1][1:-1]
            subprocess.Popen([
                "start", "cmd", "/c",
                "acfun", f"{source.routes['live']}{ac_obj.uid}", "danmaku", "--ext", f"{user_cmd[1]}"
            ], shell=True)
            cmd_log.append("danmaku")
            continue
        elif user_cmd[0] == 'like' and user_cmd[1].isdigit():
            if int(user_cmd[1]) <= 600:
                ac_obj.like(int(user_cmd[1]))
                cmd_log.append(" ".join(user_cmd))
        elif user_cmd[0] == 'push' and acer.is_logined:
            ac_obj.push_danmaku(user_cmd[1])
            cmd_log.append("push")
    console.clear()
    return None


# 详情菜单
def acfun_detail(ac_obj, act=None, ext=None):
    if ac_obj is None:
        return None
    obj_type = ac_obj.__class__.__name__
    if obj_type in ['AcLink', 'AcChannel', 'AcAlbum']:
        return None
    elif obj_type == "AcImage":
        return cli_image(ac_obj, act, ext)
    elif obj_type == 'AcVideo':
        pass
    elif obj_type == 'AcBangumi':
        pass
    elif obj_type == 'AcArticle':
        pass
    elif obj_type == 'AcUp':
        pass
    elif obj_type == "AcLiveUp":
        if act == 'danmaku':
            ac_obj.watching_danmaku(potplayer=ext)
            return None
        return cli_live(ac_obj, act, ext)
    return None


# 对象类型
# 视频，番剧，文章，用户，直播
# acfun <url> <act> <ext>
# 功能类型
# 签到，
# acfun <src> <act>


@click.command()
@click.argument('src', default='help')
@click.argument('act', default="", nargs=1)
@click.option('--ext')
@click.option('--login')
def cli(src, act=None, ext=None, login=None):
    act = None if act == "" else act
    ext = None if ext == "" else ext
    if isinstance(login, str):
        if login.count(":") == 1:
            username, password = login.split(':')
            acer.login(username, password)
        if (len(login) == 11 and login.isdigit()) or login.count("@") == 1:
            if os.path.isfile(f"{login}.cookies"):
                acer.loading(login)
    while True:
        if src == 'help':  # 帮助
            click.echo(f"Need Help?")
            return None
        elif src == 'signin':  # 签到
            acer.signin()
            return None
        elif src.startswith('http') and parse.urlsplit(src).netloc.endswith('acfun.cn'):
            result = acfun_detail(acer.get(src), act=act, ext=ext)
            return None

    pass


if __name__ == '__main__':
    cli()
