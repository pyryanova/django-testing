import pytest
from http import HTTPStatus
from django.urls import reverse
from django.contrib.auth import get_user_model

from news.models import Comment, News

User = get_user_model()


@pytest.fixture
def author():
    return User.objects.create_user(username='Комментатор')


@pytest.fixture
def reader():
    return User.objects.create_user(username='Читатель')


@pytest.fixture
def news():
    return News.objects.create(title='Заголовок', text='Текст')


@pytest.fixture
def comment(news, author):
    return Comment.objects.create(news=news, author=author, text='Комментарий')


@pytest.fixture
def comment_urls(comment):
    return {
        'edit': reverse('news:edit', args=(comment.id,)),
        'delete': reverse('news:delete', args=(comment.id,)),
        'detail': reverse('news:detail', args=(comment.news.id,))
    }


@pytest.mark.django_db
def test_pages_available_for_anonymous_user(client, news):
    """Анонимный пользователь видит главную, новость, логин, регистрацию, logout редиректит."""
    url_names = [
        ('news:home', None, HTTPStatus.OK),
        ('news:detail', (news.id,), HTTPStatus.OK),
        ('users:login', None, HTTPStatus.OK),
        ('users:signup', None, HTTPStatus.OK),
        ('users:logout', None, HTTPStatus.FOUND),
    ]
    for name, args, expected_status in url_names:
        url = reverse(name, args=args)
        response = client.get(url)
        assert response.status_code == expected_status


@pytest.mark.django_db
def test_comment_edit_and_delete_access(client, author, reader, comment):
    """Только автор комментария может редактировать и удалять его."""
    for user, expected_status in [(author, HTTPStatus.OK), (reader, HTTPStatus.NOT_FOUND)]:
        client.force_login(user)
        for action in ('news:edit', 'news:delete'):
            url = reverse(action, args=(comment.id,))
            response = client.get(url)
            assert response.status_code == expected_status


@pytest.mark.django_db
def test_anonymous_redirect_to_login(client, comment):
    """Анонимный пользователь перенаправляется на логин при попытке редактирования или удаления."""
    login_url = reverse('users:login')
    for action in ('news:edit', 'news:delete'):
        url = reverse(action, args=(comment.id,))
        response = client.get(url)
        expected_redirect = f'{login_url}?next={url}'
        assert response.status_code == HTTPStatus.FOUND
        assert response.url == expected_redirect
