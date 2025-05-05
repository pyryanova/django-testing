import pytest
from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm


@pytest.mark.django_db
def test_news_count(client, bulk_news):
    response = client.get(reverse('news:home'))
    object_list = response.context['object_list']
    assert len(object_list) == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, bulk_news):
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
