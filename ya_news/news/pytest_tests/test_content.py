import pytest
from datetime import timedelta

from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from news.forms import CommentForm
from news.models import Comment, News


@pytest.fixture(autouse=True)
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


@pytest.mark.django_db
def test_news_count(client):
    response = client.get(reverse('news:home'))
    object_list = response.context['object_list']
    assert len(object_list) == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client):
    response = client.get(reverse('news:home'))
    dates = [news.date for news in response.context['object_list']]
    assert dates == sorted(dates, reverse=True)


@pytest.mark.django_db
def test_comments_order(news_with_comments):
    comments = news_with_comments.comment_set.order_by('created')
    timestamps = [comment.created for comment in comments]
    assert timestamps == sorted(timestamps)


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, detail_url):
    response = client.get(detail_url)
    assert 'form' not in response.context


@pytest.mark.django_db
def test_authorized_client_has_form(author_client, detail_url):
    response = author_client.get(detail_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
