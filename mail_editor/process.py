import hashlib

from lxml import etree


def load_image(url):
    import requests
    # TODO check domains?
    # TODO check data urls
    r = requests.get(url)
    content_type = r.headers["Content-Type"]
    if not content_type.startswith("image/"):
        raise Exception("not an image file")
    return r.content, content_type


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


def process_html(html, base_url="", extract_attachments=True, fix_links=True):
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
                url = make_url_absolute(url, base_url)
                content, content_type = load_image(url)
                cid = cid_for_bytes(content)
                image_attachments[cid] = (content, content_type)
            img.set("src", f"cid:{cid}")

    if fix_links:
        for a in root.iterfind(".//a"):
            url = a.get("href")
            if not url:
                continue
            a.set("href", make_url_absolute(url, base_url))

    result = etree.tostring(root, encoding="utf8", pretty_print=False, method="html")
    attachments = [(cid, content, ct) for cid, (content, ct) in image_attachments.items()]

    return result.decode("utf8"), attachments


def cid_for_bytes(content):
    # let's hash content for de-duplication
    h = hashlib.md5()
    h.update(content)
    return h.hexdigest()


