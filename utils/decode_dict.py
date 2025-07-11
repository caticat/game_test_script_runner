import re
import urllib.parse

def looks_like_url_encoded(s):
    # 检查是否含有 % 后跟两个十六进制字符的模式
    return isinstance(s, str) and re.search(r'%[0-9A-Fa-f]{2}', s) is not None

def looks_like_misencoded_utf8(s):
    # 简单检测是否是被误解码的 UTF-8 字符串（通常表现为大量的拉丁字母和 \x）
    if not isinstance(s, str):
        return False
    try:
        decoded = s.encode('latin1').decode('utf-8')
        # 如果结果中含有中文字符，认为是误编码成功修复
        return any('\u4e00' <= ch <= '\u9fff' for ch in decoded)
    except (UnicodeEncodeError, UnicodeDecodeError):
        return False

def fix_misencoded_utf8(s):
    try:
        return s.encode('latin1').decode('utf-8')
    except Exception:
        return s

def decode_dict(data):
    if isinstance(data, dict):
        return {k: decode_dict(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [decode_dict(item) for item in data]
    elif isinstance(data, str):
        if looks_like_url_encoded(data):
            data = urllib.parse.unquote(data)
        if looks_like_misencoded_utf8(data):
            data = fix_misencoded_utf8(data)
        return data
    else:
        return data
