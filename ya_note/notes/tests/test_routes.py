from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.note = Note.objects.create(
            title='Заметка',
            text='Текст заметки',
            slug='test-note',
            author=cls.author
        )
        cls.routes_statuses = [
            ('notes:home', None, HTTPStatus.OK, cls.author, 'get'),
            ('notes:success', None, HTTPStatus.OK, cls.author, 'get'),
            ('users:login', None, HTTPStatus.OK, None, 'get'),
            ('users:signup', None, HTTPStatus.OK, None, 'get'),
            ('notes:edit', (cls.note.slug,), HTTPStatus.OK, cls.author, 'get'),
            ('notes:delete', (cls.note.slug,), HTTPStatus.OK,
             cls.author, 'get'),
            ('notes:edit', (cls.note.slug,), HTTPStatus.NOT_FOUND,
             cls.reader, 'get'),
            ('notes:delete', (cls.note.slug,), HTTPStatus.NOT_FOUND,
             cls.reader, 'get'),
            ('users:logout', None, HTTPStatus.OK, cls.author, 'post',
             'registration/logout.html'),
        ]
        cls.protected_routes = [
            ('notes:edit', (cls.note.slug,)),
            ('notes:delete', (cls.note.slug,)),
        ]

    def test_statuses_for_routes(self):
        for name, args, status, user, method, *rest in self.routes_statuses:
            if user:
                self.client.force_login(user)
            url = reverse(name, args=args)
            with self.subTest(url=url, method=method):
                response = getattr(self.client, method)(url)
                self.assertEqual(response.status_code, status)
                if rest:
                    template = rest[0]
                    self.assertTemplateUsed(response, template)
                if user:
                    self.client.logout()

    def test_redirects_for_anonymous_client(self):
        login_url = reverse('users:login')
        for name, args in self.protected_routes:
            url = reverse(name, args=args)
            expected_redirect = f'{login_url}?next={url}'
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertRedirects(response, expected_redirect)
