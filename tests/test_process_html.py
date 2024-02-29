import os
from unittest.mock import patch

from django.conf import settings
from django.test import TestCase

from mail_editor.process import (
    FileData, cid_for_bytes,
    load_image,
    make_url_absolute,
    process_html,
    read_image_file,
)


class ProcessTestCase(TestCase):
    @patch("mail_editor.process.cid_for_bytes", return_value="MY_CID")
    @patch("mail_editor.process.load_image", return_value=FileData(b"abc", "image/jpg"))
    def test_extract_images(self, m1, m2):
        html = """
            <html><body>
                <img src="foo.jpg">
            </body></html>
        """
        expected_html = """
            <html><head></head><body>
                <img src="cid:MY_CID">
            </body></html>
        """
        result = process_html(html, "https://example.com")
        self.assertHTMLEqual(result.html, expected_html)
        self.assertEqual(result.cid_attachments, [("MY_CID", b"abc", "image/jpg")])

    @patch("mail_editor.process.load_image", return_value=None)
    def test_extract_images__keeps_absolute_url_when_not_loadable(self, m):
        html = """
            <html><body>
                <img src="not_exists.jpg">
            </body></html>
        """
        expected_html = """
            <html><head></head><body>
                <img src="https://example.com/not_exists.jpg">
            </html>
        """
        result = process_html(html, "https://example.com")
        self.assertHTMLEqual(result.html, expected_html)
        self.assertEqual(result.cid_attachments, [])

    def test_fix_anchor_urls(self):
        html = """
            <html><body>
                <a href="/foo">bar</a>
                <a href="https://external.com/foo">bar</a>
            </body></html>
        """
        expected_html = """
            <html><head></head><body>
                <a href="https://example.com/foo">bar</a>
                <a href="https://external.com/foo">bar</a>
            </body></html>
        """
        result = process_html(html, "https://example.com")
        self.assertHTMLEqual(result.html, expected_html)
        self.assertEqual(result.cid_attachments, [])

    def test_inlines_css_from_style(self):
        html = """
            <html>
            <head>
                <style>h1 { color: red; }</style/>
            </head>
            <body>
                <h1>foo</h1>
            </body></html>
        """
        expected_html = """
            <html><head></head><body>
                <h1 style="color: red;">foo</h1>
            </body></html>
        """
        result = process_html(html, "https://example.com")
        self.assertHTMLEqual(result.html, expected_html)
        self.assertEqual(result.cid_attachments, [])

    def test_inlines_css_from_link(self):
        # TODO properly test both collected STATIC_ROOT and the development staticfiles.finders fallback
        html = """
            <html>
            <head>
                <link href="/static/css/style.css" rel="stylesheet" type="text/css"/>
            </head>
            <body>
                <h1>foo</h1>
            </body></html>
        """
        expected_html = """
            <html><head></head><body>
                <h1 style="color: red;">foo</h1>
            </body></html>
        """
        result = process_html(html, "https://example.com")
        self.assertHTMLEqual(result.html, expected_html)
        self.assertEqual(result.cid_attachments, [])

    def test_inline_css_from_link__removes_external_link(self):
        html = """
            <html>
            <head>
                <link href="https://external.xyz/static/css/style.css" rel="stylesheet" type="text/css"/>
            </head>
            <body>
                <h1>foo</h1>
            </body></html>
        """
        expected_html = """
            <html><head></head><body>
                <h1>foo</h1>
            </body></html>
        """
        result = process_html(html, "https://example.com")
        self.assertHTMLEqual(result.html, expected_html)
        self.assertEqual(result.cid_attachments, [])

    def test_svg(self):
        # TODO test what happens
        pass


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
            # extras
            ("http://example.com", "tel:123456789", "tel:123456789"),
            ("http://example.com", "mailto:foo@example.com", "mailto:foo@example.com"),
        ]
        for i, (base, url, expected) in enumerate(tests):
            with self.subTest((i, base, url)):
                self.assertEqual(make_url_absolute(url, base), expected)

    def test_cid_for_bytes(self):
        self.assertEqual(cid_for_bytes(b"abc"), cid_for_bytes(b"abc"))
        self.assertNotEqual(cid_for_bytes(b"123"), cid_for_bytes(b"abc"))

    def test_read_image_file(self):
        with self.subTest("exists"):
            path = os.path.join(settings.STATIC_ROOT, "logo.png")
            with open(path, "rb") as f:
                expected = f.read()

            data = read_image_file(path)
            self.assertEqual(data.content, expected)
            self.assertEqual(data.content_type, "image/png")

        with self.subTest("not exists"):
            path = os.path.join(settings.STATIC_ROOT, "not_exists.png")

            data = read_image_file(path)
            self.assertIsNone(data)

    def test_load_image(self):
        # TODO properly test both collected STATIC_ROOT and the development staticfiles.finders fallback

        static_url = make_url_absolute(settings.STATIC_URL, "http://testserver")
        media_url = make_url_absolute(settings.MEDIA_URL, "http://testserver")

        with self.subTest("static & png"):
            with open(os.path.join(settings.STATIC_ROOT, "logo.png"), "rb") as f:
                expected = f.read()

            data = load_image(
                "/static/logo.png", "http://testserver", static_url, media_url
            )
            self.assertEqual(data.content, expected)
            self.assertEqual(data.content_type, "image/png")

        with self.subTest("media & jpg"):
            with open(os.path.join(settings.MEDIA_ROOT, "logo.jpg"), "rb") as f:
                expected = f.read()

            data = load_image(
                "/media/logo.jpg", "http://testserver", static_url, media_url
            )
            self.assertEqual(data.content, expected)
            self.assertEqual(data.content_type, "image/jpeg")

        with self.subTest("not exists"):
            data = load_image(
                "/static/not_exists.png", "http://testserver", static_url, media_url
            )
            self.assertIsNone(data)
