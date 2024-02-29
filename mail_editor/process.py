import hashlib
import os
from mimetypes import guess_type
from typing import NamedTuple, Optional
from urllib.parse import urlparse
from urllib.request import urlopen

from django.conf import settings
from django.contrib.staticfiles import finders

import css_inline
from lxml import etree

"""
notes: for attaching and inlining STATIC and MEDIA is hardcoded to FileSystemStorage
"""

FILE_ROOT = settings.DJANGO_PROJECT_DIR

supported_types = [
    "image/jpeg",
    "image/png",
    # add webp?
    # NOT SVG!
]


class FileData(NamedTuple):
    content: bytes
    content_type: str


class CIDAttachment(NamedTuple):
    cid: str
    content: bytes
    content_type: str


class ProcessedHTML(NamedTuple):
    html: str
    cid_attachments: list[CIDAttachment]


def process_html(
    html: str,
    base_url: str,
    extract_attachments: bool = True,
    inline_css: bool = True,
) -> ProcessedHTML:
    # TODO handle errors in cosmetics and make sure we always produce something
    parser = etree.HTMLParser()
    root = etree.fromstring(html, parser)

    static_url = make_url_absolute(settings.STATIC_URL, base_url)
    media_url = make_url_absolute(settings.MEDIA_URL, base_url)

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
                data = load_image(url, base_url, static_url, media_url)
                if not data:
                    # if we can't load the image leave element as-is and remember bad url
                    url_cid_cache[url] = None
                    continue
                cid = cid_for_bytes(data.content)
                url_cid_cache[url] = cid
                image_attachments[cid] = CIDAttachment(
                    cid, data.content, data.content_type
                )

            elem.set("src", f"cid:{cid}")

    if inline_css:
        for elem in root.iterfind(".//link"):
            url = elem.get("href")
            if not url:
                continue
            # resolving back to paths is needed so css-inliner can use a file:// base_url
            partial_file_path = _find_static_path_for_inliner(url, static_url)
            if partial_file_path:
                elem.set("href", partial_file_path)
            else:
                # remove this element because we don't want to load external stylesheets
                elem.getparent().remove(elem)

    result = etree.tostring(
        root, encoding="utf8", pretty_print=False, method="html"
    ).decode("utf8")

    if inline_css:
        result = _html_inline_css(result)

    # TODO support inlining CSS referenced images?

    return ProcessedHTML(result, list(image_attachments.values()))


def cid_for_bytes(content: bytes) -> str:
    h = hashlib.sha1(usedforsecurity=False)
    h.update(content)
    return h.hexdigest()


def load_image(
    url: str, base_url: str, static_url: str, media_url: str
) -> Optional[FileData]:
    # TODO support data urls? steal from mailcleaner
    data = None

    url = make_url_absolute(url, base_url)

    if url.startswith("data:"):
        data = read_data_uri(url)

    elif url.startswith(static_url):
        file_name = url[len(static_url) :]
        file_path = os.path.join(settings.STATIC_ROOT, file_name)

        data = read_image_file(file_path)
        if not data:
            # fallback for development
            file_path = finders.find(file_name)
            if file_path:
                data = read_image_file(file_path)

    elif url.startswith(media_url):
        file_name = url[len(media_url) :]
        file_path = os.path.join(settings.MEDIA_ROOT, file_name)

        data = read_image_file(file_path)
    # else:
    #   NOTE: loading from http is currently not supported because of http overhead
    #     url = make_url_absolute(base_url)
    #     # TODO check domains?
    #     # TODO check status
    #     # TODO handle errors
    #     r = requests.get(url)
    #     content_type = r.headers["Content-Type"]
    #     content = r.content

    if data and data.content and data.content_type in supported_types:
        return data
    else:
        # TODO lets log/?
        return None


def read_data_uri(uri: str) -> Optional[FileData]:
    assert uri.startswith("data:")

    try:
        with urlopen(uri) as response:
            content = response.read()
            content_type = response.headers.get("Content-Type")
            if content and content_type:
                return FileData(content, content_type)
    except Exception:
        # TODO stricter exception types
        # we never want errors to block important mail
        # maybe we should log though
        pass

    return None


def read_image_file(path: str) -> Optional[FileData]:
    try:
        with open(path, "rb") as f:
            content = f.read()
        # is guess_type() what we want or do we look in the content?
        content_type, _encoding = guess_type(path)
        return FileData(content, content_type)
    except Exception:
        # TODO stricter exception types
        # we never want errors to block important mail
        # maybe we should log though
        return None


def make_url_absolute(url: str, base_url: str = "") -> str:
    """
    base_url: https://domain
    """
    # TODO we're using the path part as file path so we should handle sneaky attempts to use relative ".."
    try:
        parse = urlparse(url)
        # allow tel:, mailto: links
        if parse.scheme and parse.scheme not in ("http", "https"):
            return url
    except ValueError:
        pass

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


def _html_inline_css(html: str) -> str:
    inliner = css_inline.CSSInliner(
        inline_style_tags=True,
        keep_style_tags=False,
        keep_link_tags=False,
        extra_css=None,
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


def _find_static_path_for_inliner(url: str, static_url: str) -> Optional[str]:
    if url.startswith(static_url):
        file_name = url[len(static_url) :]
        file_path = os.path.join(settings.STATIC_ROOT, file_name)
        if os.path.exists(file_path):
            return str(os.path.relpath(file_path, start=FILE_ROOT))
        else:
            file_path = finders.find(file_name)
            if file_path:
                return str(os.path.relpath(file_path, start=FILE_ROOT))

    # we don't allow external links
    return None
