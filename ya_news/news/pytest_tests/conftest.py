from datetime import timedelta

import pytest

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News

User = get_user_model()


@pytest.fixture(autouse=True)
@pytest.mark.django_db
def enable_db_access_for_all_tests():
    pass


@pytest.fixture
def author():
    return User.objects.create_user(username='Комментатор')


@pytest.fixture
def reader():
    return User.objects.create_user(username='Читатель')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader):
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def news():
    return News.objects.create(title='Заголовок', text='Текст')


@pytest.fixture
def news_list():
    return [
        News.objects.create(title=f'Новость {i}', text='Текст')
        for i in range(5)
    ]


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


@pytest.fixture
def news_urls(news):
    return {
        'home': reverse('news:home'),
        'detail': reverse('news:detail', args=(news.id,))
    }


@pytest.fixture
def user_urls():
    return {
        'login': reverse('users:login'),
        'signup': reverse('users:signup'),
        'logout': reverse('users:logout')
    }


@pytest.fixture
def bulk_news():
    today = timezone.now().date()
    return News.objects.bulk_create([
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        ) for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ])


@pytest.fixture
def news_with_comments(author):
    news_item = News.objects.create(
        title='Тестовая новость',
        text='Просто текст.'
    )
    now = timezone.now()
    for index in range(10):
        comment = Comment.objects.create(
            news=news_item,
            author=author,
            text=f'Tекст {index}'
        )
        comment.created = now + timedelta(minutes=index)
        comment.save()
    return news_item


@pytest.fixture
def detail_url(news_with_comments):
    return reverse('news:detail', args=(news_with_comments.id,))
