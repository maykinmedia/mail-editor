import os

from django.conf import settings
from django.test import TestCase

from mail_editor.process import cid_for_bytes, load_image, make_url_absolute, process_html

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


class ProcessTestCase(TestCase):
    @patch("mail_editor.process.cid_for_bytes", return_value="MY_CID")
    @patch("mail_editor.process.load_image", return_value=(b"abc", "image/jpg"))
    def test_extract_images(self, m1, m2):
        html = '<html><body><p><img src="foo.jpg"></p></body></html>'
        result, objects = process_html(html, "https://example.com")

        expected_html = '<html><head></head><body><p><img src="cid:MY_CID"></p></body></html>'

        self.assertEqual(result.rstrip(), expected_html)
        self.assertEqual(objects, [("MY_CID", b"abc", "image/jpg")])

    def test_fix_anchor_urls(self):
        html = '<html><body><p><a href="/foo">bar</a></p></body></html>'
        result, objects = process_html(html, "https://example.com")

        expected_html = '<html><head></head><body><p><a href="https://example.com/foo">bar</a></p></body></html>'

        self.assertEqual(result.rstrip(), expected_html)
        self.assertEqual(objects, [])

    def test_fix_link_urls(self):
        html = '<html><body><link href="/foo.css"></body></html>'
        result, objects = process_html(html, "https://example.com")

        expected_html = '<html><head></head><body><link href="https://example.com/foo.css"></body></html>'

        self.assertEqual(result.rstrip(), expected_html)
        self.assertEqual(objects, [])

    def test_inline_css_link(self):
        # TODO properly test both collected STATIC_ROOT and the development staticfiles.finders fallback

        html = '<html><head><link href="/static/css/style.css" rel="stylesheet" type="text/css"/></head><body><h1>foo</h1></body></html>'
        result, objects = process_html(html, "https://example.com")

        expected_html = '<html><head></head><body><h1 style="color: red;">foo</h1></body></html>'

        self.assertEqual(result.rstrip(), expected_html)
        self.assertEqual(objects, [])


class ProcessHelpersTestCase(TestCase):
    def test_make_url_absolute(self):
        tests = [
            ("http://example.com", "/foo", "http://example.com/foo"),
            ("http://example.com", "foo", "http://example.com/foo"),
            ("http://example.com", "", "http://example.com"),
            ("http://example.com", "http://example.com/foo", "http://example.com/foo"),
            ("http://example.com", "", "http://example.com"),
            ("", "http://example.com/foo", "http://example.com/foo"),
            ("", "foo", "/foo"),
            ("", "", "/"),
        ]
        for i, (base, url, expected) in enumerate(tests):
            with self.subTest((i, base, url)):
                self.assertEqual(make_url_absolute(url, base), expected)

    def test_cid_for_bytes(self):
        self.assertEqual(cid_for_bytes(b"abc"), cid_for_bytes(b"abc"))
        self.assertNotEqual(cid_for_bytes(b"123"), cid_for_bytes(b"abc"))

    def test_load_image(self):
        # TODO properly test both collected STATIC_ROOT and the development staticfiles.finders fallback

        with self.subTest("static & png"):
            with open(os.path.join(settings.STATIC_ROOT, 'logo.png'), "rb") as f:
                expected = f.read()

            actual, content_type = load_image("/static/logo.png","http://testserver")
            self.assertEqual(actual, expected)
            self.assertEqual(content_type, "image/png")

        with self.subTest("media & jpg"):
            with open(os.path.join(settings.MEDIA_ROOT, 'logo.jpg'), "rb") as f:
                expected = f.read()

            actual, content_type = load_image("/media/logo.jpg", "http://testserver")
            self.assertEqual(actual, expected)
            self.assertEqual(content_type, "image/jpeg")
