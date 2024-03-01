import base64
import os

from django.conf import settings
from django.test import TestCase

from mail_editor.process import (
    cid_for_bytes,
    load_image,
    make_url_absolute,
    read_data_uri,
    read_image_file,
)


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
            (
                "http://example.com",
                "data:image/png;base64,xyz",
                "data:image/png;base64,xyz",
            ),
        ]
        for i, (base, url, expected) in enumerate(tests):
            with self.subTest((i, base, url)):
                self.assertEqual(make_url_absolute(url, base), expected)

    def test_cid_for_bytes(self):
        self.assertEqual(cid_for_bytes(b"abc"), cid_for_bytes(b"abc"))
        self.assertNotEqual(cid_for_bytes(b"12356"), cid_for_bytes(b"abc"))

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

    def test_read_data_uri(self):
        path = os.path.join(settings.STATIC_ROOT, "logo.png")
        with open(path, "rb") as f:
            png_data = f.read()
            png_b64 = base64.b64encode(png_data).decode("utf8")

        with self.subTest("valid"):
            datauri = f"data:image/png;base64,{png_b64}"
            data = read_data_uri(datauri)
            self.assertEqual(data.content, png_data)
            self.assertEqual(data.content_type, "image/png")

        with self.subTest("bad content"):
            datauri = "data:image/png;base64,xxxxxxxxxxx"
            data = read_data_uri(datauri)
            self.assertIsNone(data)

    def test_load_image(self):
        # TODO properly test both collected STATIC_ROOT and the development staticfiles.finders fallback

        static_url = make_url_absolute(settings.STATIC_URL, "http://testserver")
        media_url = make_url_absolute(settings.MEDIA_URL, "http://testserver")

        with self.subTest("static URL & PNG"):
            with open(os.path.join(settings.STATIC_ROOT, "logo.png"), "rb") as f:
                expected = f.read()

            data = load_image(
                "/static/logo.png", "http://testserver", static_url, media_url
            )
            self.assertEqual(data.content, expected)
            self.assertEqual(data.content_type, "image/png")

        with self.subTest("static URL & SVG"):
            data = load_image(
                "/static/image.svg", "http://testserver", static_url, media_url
            )
            self.assertIsNone(data)

        with self.subTest("media URL & JPG"):
            with open(os.path.join(settings.MEDIA_ROOT, "logo.jpg"), "rb") as f:
                expected = f.read()

            data = load_image(
                "/media/logo.jpg", "http://testserver", static_url, media_url
            )
            self.assertEqual(data.content, expected)
            self.assertEqual(data.content_type, "image/jpeg")

        with self.subTest("datauri & PNG"):
            path = os.path.join(settings.STATIC_ROOT, "logo.png")
            with open(path, "rb") as f:
                png_data = f.read()
                png_b64 = base64.b64encode(png_data).decode("utf8")

            data = load_image(
                f"data:image/png;base64,{png_b64}",
                "http://testserver",
                static_url,
                media_url,
            )
            self.assertEqual(data.content, png_data)
            self.assertEqual(data.content_type, "image/png")

        with self.subTest("datauri & SVG"):
            path = os.path.join(settings.STATIC_ROOT, "image.svg")
            with open(path, "rb") as f:
                svg_data = f.read()
                svg_b64 = base64.b64encode(svg_data).decode("utf8")

            data = load_image(
                f"data:image/svg+xml;base64,{svg_b64}",
                "http://testserver",
                static_url,
                media_url,
            )
            self.assertIsNone(data)

        with self.subTest("static not exists"):
            data = load_image(
                "/static/not_exists.png", "http://testserver", static_url, media_url
            )
            self.assertIsNone(data)

        with self.subTest("media not exists"):
            data = load_image(
                "/media/not_exists.png", "http://testserver", static_url, media_url
            )
            self.assertIsNone(data)
