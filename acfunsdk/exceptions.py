# coding=utf-8
from functools import wraps

__all__ = (
    'need_login',
    'not_404',
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


def not_404(f):
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        if self.__class__.__name__ in ["AcBangumi", "AcVideo", "AcArticle", "AcAlbum", "AcUp", "AcMoment"]:
            if self.is_404 is True:
                raise ShuiNi("水逆 (你想要的并不存在)")
        return f(self, *args, **kwargs)
    return wrapper


class AcExploded(ConnectionError):
    """阿禅爆炸 (今天A站挂了吗？)"""
    def __init__(self, message: str, url: str = None, status_code: int = None):
        super().__init__(message)
        self.url = url
        self.status_code = status_code


class NotInCar(PermissionError):
    """没上车 (尚未登录)"""
    def __init__(self, message: str = "先登录啊！"):
        super().__init__(message)


class ShuiNi(FileNotFoundError):
    """水逆 (404被删掉)"""
    def __init__(self, message: str = "水逆 (你想要的并不存在)", resource_id: str = None):
        super().__init__(message)
        self.resource_id = resource_id


class NiShuiA(PermissionError):
    """你谁啊 (非本人无权操作)"""


class LuanJiangHua(ConnectionRefusedError):
    """乱讲话 (401被服务器拒绝)"""


class TingBuDong(ValueError):
    """听不懂 (数据格式已变更)"""
