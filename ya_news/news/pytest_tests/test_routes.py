import pytest
from http import HTTPStatus
from pytest_lazyfixture import lazy_fixture

AUTHOR_CLIENT = lazy_fixture('author_client')
READER_CLIENT = lazy_fixture('reader_client')
CLIENT = lazy_fixture('client')
COMMENT_URLS = lazy_fixture('comment_urls')
NEWS_URLS = lazy_fixture('news_urls')
USER_URLS = lazy_fixture('user_urls')


@pytest.mark.django_db
@pytest.mark.parametrize(
    'client_fixture,url_fixture,expected_status', [
        (CLIENT, 'home', HTTPStatus.OK),
        (CLIENT, 'detail', HTTPStatus.OK),
        (CLIENT, 'login', HTTPStatus.OK),
        (CLIENT, 'signup', HTTPStatus.OK),
        (CLIENT, 'logout', HTTPStatus.FOUND),
        (AUTHOR_CLIENT, 'edit', HTTPStatus.OK),
        (AUTHOR_CLIENT, 'delete', HTTPStatus.OK),
        (READER_CLIENT, 'edit', HTTPStatus.NOT_FOUND),
        (READER_CLIENT, 'delete', HTTPStatus.NOT_FOUND),
    ]
)
def test_pages_statuses(
    client_fixture,
    url_fixture,
    expected_status,
    comment_urls, news_urls, user_urls
):
    url_sources = {
        'edit': comment_urls['edit'],
        'delete': comment_urls['delete'],
        'detail': news_urls['detail'],
        'home': news_urls['home'],
        'login': user_urls['login'],
        'signup': user_urls['signup'],
        'logout': user_urls['logout'],
    }
    url = url_sources[url_fixture]
    response = client_fixture.get(url)
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize('name', ['edit', 'delete'])
def test_redirects_for_anonymous(client, comment_urls, user_urls, name):
    url = comment_urls[name]
    expected_redirect = f'{user_urls['login']}?next={url}'
    response = client.get(url)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == expected_redirect
