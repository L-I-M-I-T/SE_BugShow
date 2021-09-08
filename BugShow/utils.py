import re
import hashlib
import psutil
import random

from urllib.parse import urlparse, urljoin
from flask import request, url_for, redirect

def get_md5(text):
    return hashlib.md5(text.encode()).hexdigest()

def validate_username(username):
    r = re.match('^[a-zA-Z0-9_]*$', username)
    return True if r else False

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

def redirect_back(default='index_bp.index', **kwargs):
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)
    return redirect(url_for(default, **kwargs))

def get_text_plain(html_text):
    from bs4 import BeautifulSoup
    bs = BeautifulSoup(html_text, 'html.parser')
    return bs.get_text()

def get_md5(text):
    return hashlib.md5(text.encode()).hexdigest()

def hardware_monitor():
    cpu_per = psutil.cpu_percent()
    me_per = psutil.virtual_memory().percent
    return cpu_per, me_per

def generate_ver_code():
    str = ""
    for i in range(6):
        ch = chr(random.randrange(ord('0'), ord('9') + 1))
        str += ch
    return str
