import hashlib
import itertools
import os
from mimetypes import guess_type

import css_inline
import requests
from lxml import etree

from django.conf import settings


def read_image_file(path):
    with open(path, "rb") as f:
        content = f.read()
    content_type, _encoding = guess_type(path)
    return content, content_type


def load_image(url, base_url):
    # TODO support data urls?
    # TODO handle errors
    # TODO use storage backend API instead of manually building paths etc
    # TODO ~~support more storage backends~~
    # TODO refactor because this looks bad
    if url.startswith(settings.STATIC_URL):
        url = url[len(settings.STATIC_URL):]
        url = os.path.join(settings.STATIC_ROOT, url)

        content, content_type = read_image_file(url)

    elif url.startswith(settings.MEDIA_URL):
        url = url[len(settings.MEDIA_URL):]
        url = os.path.join(settings.MEDIA_ROOT, url)

        content, content_type = read_image_file(url)
    else:
        url = make_url_absolute(base_url)
        # TODO check domains?
        r = requests.get(url)
        content_type = r.headers["Content-Type"]
        content = r.content

    if not content_type.startswith("image/"):
        # TODO lets not blow-up
        raise Exception("not an image file")
    return content, content_type


def make_url_absolute(url, base_url=""):
    """
    base_url: https://domain
    """
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


def html_inline_css(html):
    inliner = css_inline.CSSInliner(
        inline_style_tags=True,
        keep_style_tags=False,
        keep_link_tags=False,
        load_remote_stylesheets=False,
        extra_css=None,
        base_url=f"file://{settings.STATIC_ROOT}",
    )
    html = inliner.inline(html)
    return html


def process_html(html, base_url="", extract_attachments=True, inline_css=True):
    parser = etree.HTMLParser()
    root = etree.fromstring(html, parser)

    image_attachments = dict()
    url_cid_cache = dict()

    if extract_attachments:
        # extract and swap related content ID's
        for img in root.iterfind(".//img"):
            url = img.get("src")
            if not url:
                continue
            # cache cid & content for deduplication (eg: icons)
            if url in url_cid_cache:
                cid = url_cid_cache[url]
            else:
                content, content_type = load_image(url, base_url)
                cid = cid_for_bytes(content)
                image_attachments[cid] = (content, content_type)
            img.set("src", f"cid:{cid}")

    fix_attribs = [
        (".//a", "href"),
    ]
    if not extract_attachments:
        fix_attribs += [
            (".//img", "src"),
        ]
    if not inline_css:
        fix_attribs += [
            (".//link", "href"),
        ]

    for selector, attr in fix_attribs:
        for elem in root.iterfind(selector):
            url = elem.get(attr)
            if not url:
                continue
            elem.set(attr, make_url_absolute(url, base_url))

    if inline_css:
        for href_elem in root.iterfind(".//link"):
            url = href_elem.get("href")
            if not url:
                continue
            if url.startswith(settings.STATIC_URL):
                # this is needed so css-inliner's can use a file:// base_url
                url = url[len(settings.STATIC_URL)]
                href_elem.set("href", url)
            else:
                href_elem.set("href", make_url_absolute(url, base_url))

    result = etree.tostring(root, encoding="utf8", pretty_print=False, method="html").decode("utf8")

    if inline_css:
        result = html_inline_css(result)

    attachments = [(cid, content, ct) for cid, (content, ct) in image_attachments.items()]

    return result, attachments


def cid_for_bytes(content):
    # let's hash content for de-duplication
    h = hashlib.md5()
    h.update(content)
    return h.hexdigest()


