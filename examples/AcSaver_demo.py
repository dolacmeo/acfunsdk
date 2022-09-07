# coding=utf-8
import os
from acfunsdk import Acer

# 实例化一个Acer
acer = Acer(debug=True)

# 首次使用: 以Windows平台举例
# 定义保存路径
saver_path = r"D:\AcSaver"


def first_run():
    # 实例化AcSaver父类
    acsaver = acer.AcSaver(saver_path)
    # 实例化后 会在路径下生成 index.html

    # github下载静态文件
    # https://github.com/dolaCmeo/acfunSDK/tree/assets
    acsaver.download_assets_from_github()

    # 下载所有Ac表情资源
    acsaver.save_emot()


# 保存视频
def save_video(link):
    demo_video = acer.get(link)
    demo_video.saver(saver_path).save_all()
    # 保存以下内容
    # 1. 视频.mp4 , 如有分P则全部保存在单独的mp4
    # 2. 弹幕，并转换成ass，本地播放器可直接观看
    # 3. 评论，100页分P，保存包括评论中可正常访问的图片


# 保存文章
def save_article(link):
    demo_article = acer.get(link)
    demo_article.saver(saver_path).save_all()
    # 保存以下内容
    # 1. 视频.mp4 , 如有分P则全部保存在单独的mp4
    # 2. 评论，100页分P，保存包括评论中可正常访问的图片

# 保存番剧(暂未支持)
# 保存直播(暂未支持)


# 查看保存列表
print("SaverIndex:", os.path.join(saver_path, 'index.html'))

if __name__ == '__main__':
    first_run()
    # video_link = "https://www.acfun.cn/v/ac4741185"
    # save_video(video_link)
    # article_link = "https://www.acfun.cn/a/ac32633020"
    # save_article(article_link)
    pass
