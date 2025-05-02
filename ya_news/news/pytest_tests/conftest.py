from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News

User = get_user_model()


@pytest.fixture
def author():
    return User.objects.create_user(username='Комментатор')


@pytest.fixture
def news_item():
    return News.objects.create(title='Тестовая новость', text='Просто текст.')


@pytest.fixture
def comments(author, news_item):
    now = timezone.now()
    comment_list = []
    for index in range(10):
        comment = Comment.objects.create(
            news=news_item,
            author=author,
            text=f'Tекст {index}'
        )
        comment.created = now + timedelta(minutes=index)
        comment.save()
        comment_list.append(comment)
    return comment_list


@pytest.fixture
def detail_url(news_item):
    return reverse('news:detail', args=(news_item.id,))
