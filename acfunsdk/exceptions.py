# coding=utf-8
from functools import wraps

__all__ = (
    'need_login',
    'AcExploded',
    'NotInCar',
    'ShuiNi',
    'NiShuiA',
    'LuanJiangHua',
    'TingBuDong'
)


def need_login(f):
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        if self.__class__.__name__ == 'Acer':
            logined = self.is_logined
        else:
            logined = self.acer.is_logined
        if logined is False:
            raise NotInCar("先登录啊！")
        return f(self, *args, **kwargs)
    return wrapper


class AcExploded(ConnectionError):
    """阿禅爆炸 (今天A站挂了吗？)"""


class NotInCar(PermissionError):
    """没上车 (尚未登录)"""


class ShuiNi(FileNotFoundError):
    """水逆 (404被删掉)"""


class NiShuiA(PermissionError):
    """你谁啊 (非本人无权操作)"""


class LuanJiangHua(ConnectionRefusedError):
    """乱讲话 (401被服务器拒绝)"""


class TingBuDong(ValueError):
    """听不懂 (数据格式已变更)"""
