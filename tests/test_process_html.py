from unittest.mock import patch

from django.test import TestCase

from mail_editor.process import FileData, process_html


class ProcessTestCase(TestCase):
    """
    note the patched helpers are individually and more exhaustively tested elsewhere
    """

    @patch("mail_editor.process.cid_for_bytes", return_value="MY_CID", autospec=True)
    @patch(
        "mail_editor.process.load_image",
        return_value=FileData(b"abc", "image/jpg"),
        autospec=True,
    )
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

    @patch("mail_editor.process.load_image", return_value=None, autospec=True)
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
                <a href="/foo">foo</a>
                <a href="https://external.com/bar">bar</a>
            </body></html>
        """
        expected_html = """
            <html><head></head><body>
                <a href="https://example.com/foo">foo</a>
                <a href="https://external.com/bar">bar</a>
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
