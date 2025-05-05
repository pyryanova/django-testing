from http import HTTPStatus

from .common import NotesTestBase, LOGIN_URL


class TestRoutes(NotesTestBase):
    def test_statuses_for_routes(self):
        urls_statuses = (
            (self.author_client, self.list_url, HTTPStatus.OK),
            (self.author_client, self.detail_url, HTTPStatus.OK),
            (self.author_client, self.create_url, HTTPStatus.OK),
            (self.author_client, self.edit_url, HTTPStatus.OK),
            (self.author_client, self.delete_url, HTTPStatus.OK),
            (self.reader_client, self.edit_url, HTTPStatus.NOT_FOUND),
            (self.reader_client, self.delete_url, HTTPStatus.NOT_FOUND),
        )
        for client, url, expected_status in urls_statuses:
            with self.subTest(url=url):
                response = client.get(url)
                self.assertEqual(response.status_code, expected_status)

    def test_redirects_for_anonymous_client(self):
        urls = (
            self.list_url,
            self.create_url,
            self.edit_url,
            self.delete_url,
        )
        for url in urls:
            with self.subTest(url=url):
                expected_url = f'{LOGIN_URL}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, expected_url)
