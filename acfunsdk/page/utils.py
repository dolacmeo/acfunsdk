# coding=utf-8
import re
import base64
from uuid import uuid4
from datetime import timedelta
from acfunsdk.source import routes, apis

__author__ = 'dolacmeo'


class B64s:
    STANDARD = b'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
    EN_TRANS = STANDARD
    DE_TRANS = STANDARD

    def __init__(self, s: [bytes, bytearray], n: [int, None] = None):
        self.raw = s
        if isinstance(n, int):
            n = n % 64
            new = self.STANDARD[n:] + self.STANDARD[:n]
            self.EN_TRANS = bytes.maketrans(self.STANDARD, new)
            self.DE_TRANS = bytes.maketrans(new, self.STANDARD)

    def b64encode(self):
        return base64.standard_b64encode(self.raw).translate(self.EN_TRANS)

    def b64decode(self):
        return base64.b64decode(self.raw.translate(self.DE_TRANS))


def sizeof_fmt(num, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f} {unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f} Yi{suffix}"


def match1(text, *patterns):
    """Scans through a string for substrings matched some patterns (first-subgroups only).

    Args:
        text: A string to be scanned.
        patterns: Arbitrary number of regex patterns.

    Returns:
        When only one pattern is given, returns a string (None if no match found).
        When more than one pattern are given, returns a list of strings ([] if no match found).
    """

    if len(patterns) == 1:
        pattern = patterns[0]
        match = re.search(pattern, text)
        if match:
            return match.group(1)
        else:
            return None
    else:
        ret = []
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                ret.append(match.group(1))
        return ret


def matchall(text, patterns):
    """Scans through a string for substrings matched some patterns.

    Args:
        text: A string to be scanned.
        patterns: a list of regex pattern.

    Returns:
        a list if matched. empty if not.
    """

    ret = []
    for pattern in patterns:
        match = re.findall(pattern, text)
        ret += match

    return ret


def image_uploader(client, image_data: bytes, ext: str = 'jpeg'):
    token_req = client.post(apis['image_upload_gettoken'], data=dict(fileName=uuid4().hex.upper() + f'.{ext}'))
    token_data = token_req.json()
    assert token_data.get('result') == 0
    resume_req = client.get(apis['image_upload_resume'], params=dict(upload_token=token_data['info']['token']))
    resume_data = resume_req.json()
    assert resume_data.get('result') == 1
    fragment_req = client.post(apis['image_upload_fragment'], data=image_data,
                               params=dict(upload_token=token_data['info']['token'], fragment_id=0),
                               headers={"Content-Type": "application/octet-stream"})
    fragment_data = fragment_req.json()
    assert fragment_data.get('result') == 1
    complete_req = client.post(apis['image_upload_complete'],
                               params=dict(upload_token=token_data['info']['token'], fragment_count=1))
    complete_data = complete_req.json()
    assert complete_data.get('result') == 1
    result_req = client.post(apis['image_upload_geturl'], data=dict(token=token_data['info']['token']))
    result_data = result_req.json()
    assert result_data.get('result') == 0
    return result_data.get('url')


def limit_string(s, n):
    s = s[:n]
    if len(s) == n:
        s = s[:-2] + "..."
    return s


def thin_string(_string: str, no_break: bool = False):
    final_str = list()
    for line in _string.replace('\r', '').split('\n'):
        new_line = ' '.join(line.split()).strip()
        if len(new_line):
            final_str.append(new_line)
    if no_break is True:
        return " ".join(final_str)
    return " ↲ ".join(final_str)


def warp_mix_chars(_string: str, lens: int = 40, border: [tuple, None] = None):
    output = list()
    tmp_string = ""
    tmp_count = 0
    for i, _char in enumerate(_string):
        char_count = 2 if '\u4e00' <= _char <= '\u9fcc' else 1
        if tmp_count + char_count > lens:
            tmp_string += ' ' * (lens - tmp_count)
            output.append(tmp_string)
            tmp_string = ""
            tmp_count = 0
        tmp_string += _char
        tmp_count += char_count
    if tmp_count != 0:
        tmp_string += ' ' * (lens - tmp_count)
        output.append(tmp_string)
    if isinstance(border, tuple) and len(border) == 2:
        output = [f"{border[0]}{x}{border[1]}" for x in output]
    return output


def get_channel_info(html):
    rex = re.compile(r'\{subChannelId:(\d+),subChannelName:\"((?:(?!").)*)\"}')
    result = rex.findall(html)
    if result is not None:
        return {"subChannelId": result[0][0], "subChannelName": result[0][1]}
    return {}


def ms2time(ms: int):
    d = timedelta(milliseconds=ms)
    return str(d).split('.')[0]


def get_page_pagelets(page_obj):
    data = list()
    for item in page_obj.select("[id^=pagelet_]"):
        data.append(item.attrs['id'])
    if len(data):
        data.append('footer')
    return data


def url_complete(url):
    if isinstance(url, str):
        if url.startswith('//'):
            url = f"https:{url}"
        elif not url.startswith('http'):
            url = f"{routes['index']}{url}"
    return url
