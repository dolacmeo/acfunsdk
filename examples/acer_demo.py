# coding=utf-8
from acfunsdk import Acer

# 初始化acer

# 默认实例化
acer = Acer()
# 实例化时初次登录 (成功登录后会自动保存 '<用户名>.cookies')
# acer = Acer(username='you@email.com', password='balalabalala')
# 实例化时载入已登录cookies
# acer = Acer(loading='13800138000')
# 设置默认保存路径
# saver_path = r"D:\AcSaver"
# acer = Acer(acsaver_path=saver_path)

# ############## 主功能 ############## #
# 获取ac内容对象
# 通过链接直接获取内容对象
# 目前支持 9种内容类型：
# 视  频: https://www.acfun.cn/v/ac4741185
demo_video = acer.get("https://www.acfun.cn/v/ac4741185")
print(demo_video)
# 文  章: https://www.acfun.cn/a/ac37416587
demo_article = acer.get("https://www.acfun.cn/a/ac37416587")
print(demo_article)
# 合  集: https://www.acfun.cn/a/aa6001205
demo_album = acer.get("https://www.acfun.cn/a/aa6001205")
print(demo_album)
# 番  剧: https://www.acfun.cn/bangumi/aa5023295
demo_bangumi = acer.get("https://www.acfun.cn/bangumi/aa5023295")
print(demo_bangumi)
# 个人页: https://www.acfun.cn/u/39088
demo_up = acer.get("https://www.acfun.cn/u/39088")
print(demo_up)
# 动  态: https://www.acfun.cn/moment/am2797962
demo_moment = acer.get("https://www.acfun.cn/moment/am2797962")
print(demo_moment)
# 直  播: https://live.acfun.cn/live/378269
demo_live = acer.get("https://live.acfun.cn/live/378269")
print(demo_live)
# 分  享: https://m.acfun.cn/v/?ac=37086357
demo_share = acer.get("https://m.acfun.cn/v/?ac=37086357")
print(demo_share)
# 涂鸦(单页): https://hd.acfun.cn/doodle/knNWmnco.html
demo_doodle = acer.get("https://hd.acfun.cn/doodle/knNWmnco.html")

# acer 对象功能
# 登录用户(成功登录后会自动保存 '<用户名>.cookies')
# 请注意保存，防止被盗
# acer.login(username='you@email.com', password='balalabalala')
# 读取用户(读取成功登录后保存的 '<用户名>.cookies')
# acer.loading(username='13800138000')
# 退出登录状态
# acer.logout()
# Web端签到
# acer.signin()
# 修改用户签名
# acer.setup_signature("使用acfunsdk修改签名")
# 获取用户浏览历史
# acer.history(page=1, limit=10)
# 清空用户浏览历史
# acer.history_del_all()  # 空 全部;1,2 视频;3 文章
# 其他功能不建议使用，仅供内部调用
# acer.update_token()
# acer.throw_banana()
# acer.like_add()
# acer.like_delete()

# acer 可用属性
# acer.did
# acer.tokens
# acer.is_logined
# acer.referer
# acer.uid
# acer.username

# acer 对象关联类
# acer.message #  我的消息
# acer.fansclub  #  守护团
# acer.moment # 动态
# acer.follow  # 我的关注
# acer.favourite  # 我的收藏
# acer.album  # 我的收藏合集
# acer.contribute  # 稿件中心
# acer.danmaku  # 弹幕管理
# acer.bananamall  # 香蕉商城


if __name__ == '__main__':
    pass
