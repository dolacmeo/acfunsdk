import unittest
from httpx import Client
from acfunsdk import Acer
from acfunsdk.page import *

acer_username = "dolacmeo@qq.com"


class AcerCase(unittest.TestCase):

    def test_visitor_base(self):
        visitor = Acer()
        self.assertIsInstance(visitor.client, Client)
        self.assertTrue(all([visitor.did.startswith('web_'), len(visitor.did) == 20]))
        self.assertIsNone(visitor.uid)
        self.assertIsNone(visitor.username)
        self.assertIn("ssecurity", visitor.tokens)
        self.assertIn("visitor_st", visitor.tokens)
        self.assertFalse(visitor.is_logined)
        self.assertIsNone(visitor.message)
        self.assertIsNone(visitor.moment)
        self.assertIsNone(visitor.follow)
        self.assertIsNone(visitor.favourite)
        self.assertIsNone(visitor.danmaku)
        self.assertIsNone(visitor.contribute)
        self.assertIsNone(visitor.fansclub)
        self.assertIsNone(visitor.album)
        self.assertIsNone(visitor.bananamall)

    def test_user_base(self):
        user = Acer(loading=acer_username)
        self.assertIsInstance(user.client, Client)
        self.assertTrue(all([user.did.startswith('web_'), len(user.did) == 20]))
        self.assertTrue(isinstance(user.uid, int))
        self.assertTrue(isinstance(user.username, str))
        self.assertIn("ssecurity", user.tokens)
        self.assertIn("api_st", user.tokens)
        self.assertIn("api_at", user.tokens)
        self.assertTrue(user.is_logined)
        self.assertIsInstance(user.message, MyMessage)
        self.assertIsInstance(user.moment, MyMoment)
        self.assertIsInstance(user.follow, MyFollow)
        self.assertIsInstance(user.favourite, MyFavourite)
        self.assertIsInstance(user.danmaku, MyDanmaku)
        self.assertIsInstance(user.contribute, MyContribute)
        self.assertIsInstance(user.fansclub, MyFansClub)
        self.assertIsInstance(user.album, MyAlbum)
        self.assertIsInstance(user.bananamall, BananaMall)
        self.assertTrue(user.signin())
        self.assertIn("aCoinAmount", user.acoin())


if __name__ == '__main__':
    unittest.main()
