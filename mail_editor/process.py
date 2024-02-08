import hashlib
import itertools
import os
from mimetypes import guess_type

import css_inline
import requests
from django.contrib.staticfiles import finders
from lxml import etree

from django.conf import settings


"""
notes: for attaching and inlining STATIC and MEDIA is hardcoded to FileSystemStorage
"""

FILE_ROOT = settings.DJANGO_PROJECT_DIR


def _html_inline_css(html):
    inliner = css_inline.CSSInliner(
        inline_style_tags=True,
        keep_style_tags=False,
        keep_link_tags=False,
        extra_css=None,
        # only load our own static files
        load_remote_stylesheets=True,
        # link urls will have been transformed earlier
        base_url=f"file://{FILE_ROOT}/",
    )
    try:
        html = inliner.inline(html)
        return html
    except css_inline.InlineError as e:
        # we never want errors to block important mail
        # maybe we should log though
        if settings.DEBUG:
            raise e
        else:
            return html


def process_html(html, base_url, extract_attachments=True, inline_css=True):
    # TODO handle errors in cosmetics and make sure we always produce something
    parser = etree.HTMLParser()
    root = etree.fromstring(html, parser)

    static_url = make_url_absolute(settings.STATIC_URL, base_url)

    image_attachments = dict()
    url_cid_cache = dict()

    absolute_attribs = [
        (".//a", "href"),
        (".//img", "src"),
        (".//link", "href"),
    ]

    for selector, attr in absolute_attribs:
        for elem in root.iterfind(selector):
            url = elem.get(attr)
            if not url:
                continue
            elem.set(attr, make_url_absolute(url, base_url))

    if extract_attachments:
        # extract and swap related content ID's
        for elem in root.iterfind(".//img"):
            url = elem.get("src")
            if not url:
                continue
            # cache cid & content for deduplication (eg: icons)
            if url in url_cid_cache:
                cid = url_cid_cache[url]
                if cid is None:
                    # we remembered this was a bad url
                    continue
            else:
                content, content_type = load_image(url, base_url)
                if not content:
                    # if we can't load the image leave element as-is and remember bad url
                    url_cid_cache[url] = None
                    continue
                cid = cid_for_bytes(content)
                url_cid_cache[url] = cid
                image_attachments[cid] = (content, content_type)

            elem.set("src", f"cid:{cid}")

    if inline_css:
        for elem in root.iterfind(".//link"):
            url = elem.get("href")
            if not url:
                continue
            # TODO handle potential sneaky relative .. in urls?
            # url was made absolute earlier
            # this is needed so css-inliner's can use a file:// base_url
            url = _find_static_for_inliner(url, static_url)
            elem.set("href", url)

    result = etree.tostring(root, encoding="utf8", pretty_print=False, method="html").decode("utf8")

    if inline_css:
        result = _html_inline_css(result)

    attachments = [(cid, content, ct) for cid, (content, ct) in image_attachments.items()]

    return result, attachments


def cid_for_bytes(content):
    # let's hash content for de-duplication
    h = hashlib.sha1(usedforsecurity=False)
    h.update(content)
    return h.hexdigest()


def read_image_file(path):
    try:
        with open(path, "rb") as f:
            content = f.read()
        # is guess_type() what we want or do we look in the content?
        content_type, _encoding = guess_type(path)
        return content, content_type
    except Exception:
        # TODO stricter exception types
        # we never want errors to block important mail
        # maybe we should log though
        return None, ""


def _find_static_for_inliner(url, static_url):
    if url.startswith(static_url):
        file_name = url[len(static_url):]
        file_loc = os.path.join(settings.STATIC_ROOT, file_name)
        if os.path.exists(file_loc):
            return os.path.relpath(file_loc, start=FILE_ROOT)
        else:
            file_loc = finders.find(file_name)
            if file_loc:
                return os.path.relpath(file_loc, start=FILE_ROOT)

    return url


def load_image(url, base_url):
    # TODO support data urls?
    # TODO use storage backend API instead of manually building paths etc

    static_url = make_url_absolute(settings.STATIC_URL, base_url)
    media_url = make_url_absolute(settings.MEDIA_URL, base_url)
    content, content_type = None, ""

    url = make_url_absolute(url, base_url)

    if url.startswith(static_url):
        file_name = url[len(static_url):]
        file_path = os.path.join(settings.STATIC_ROOT, file_name)

        content, content_type = read_image_file(file_path)
        if not content:
            # fallback for development
            file_path = finders.find(file_name)
            if file_path:
                content, content_type = read_image_file(file_path)

    elif url.startswith(media_url):
        file_name = url[len(media_url):]
        file_path = os.path.join(settings.MEDIA_ROOT, file_name)

        content, content_type = read_image_file(file_path)
    # else:
    #     url = make_url_absolute(base_url)
    #     # TODO check domains?
    #     # TODO check status
    #     # TODO handle errors
    #     r = requests.get(url)
    #     content_type = r.headers["Content-Type"]
    #     content = r.content

    if not content or not content_type.startswith("image/"):
        # TODO lets log
        return None, ""
    else:
        return content, content_type


def make_url_absolute(url, base_url=""):
    """
    base_url: https://domain
    """
    # TODO surely there is a standard and proper way to do this?
    # TODO we're using the path part as file path so we should handle sneaky attempts to use relative ".."
    base_url = base_url.rstrip("/")
    if not url:
        if base_url:
            return base_url
        else:
            return "/"
    if "://" in url:
        return url
    if url[0] != "/":
        url = f"/{url}"
    return base_url + url
