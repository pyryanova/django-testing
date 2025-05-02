import pytest
from http import HTTPStatus

from django.urls import reverse
from django.contrib.auth import get_user_model

from news.forms import BAD_WORDS, WARNING
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
@pytest.mark.django_db

def comment(news, author):
    return Comment.objects.create(news=news, author=author, text='Комментарий')


@pytest.fixture
@pytest.mark.django_db
def comment_urls(comment):
    return {
        'edit': reverse('news:edit', args=(comment.id,)),
        'delete': reverse('news:delete', args=(comment.id,)),
        'detail': reverse('news:detail', args=(comment.news.id,))
    }


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news):
    url = reverse('news:detail', args=(news.id,))
    response = client.post(url, data={'text': 'Анонимный комментарий'})
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_can_create_comment(client, author, news):
    client.force_login(author)
    url = reverse('news:detail', args=(news.id,))
    response = client.post(url, data={'text': 'Тестовый комментарий'})
    assert response.status_code == HTTPStatus.FOUND
    comment = Comment.objects.get()
    assert comment.text == 'Тестовый комментарий'
    assert comment.news == news
    assert comment.author == author


@pytest.mark.django_db
def test_user_cant_use_bad_words(client, author, news):
    client.force_login(author)
    url = reverse('news:detail', args=(news.id,))
    response = client.post(url, data={'text': f'Плохое слово {BAD_WORDS[0]}'})
    response.render()
    form = response.context['form']
    assert form.errors['text'][0] == WARNING
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_author_can_delete_comment(client, author, comment, comment_urls):
    client.force_login(author)
    response = client.delete(comment_urls['delete'])
    assert response.status_code == HTTPStatus.FOUND
    assert not Comment.objects.filter(id=comment.id).exists()


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(
    client,
    reader,
    comment,
    comment_urls
):
    client.force_login(reader)
    response = client.delete(comment_urls['delete'])
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.filter(id=comment.id).exists()


@pytest.mark.django_db
def test_author_can_edit_comment(client, author, comment, comment_urls):
    client.force_login(author)
    new_text = 'Обновлённый текст'
    response = client.post(comment_urls['edit'], data={'text': new_text})
    assert response.status_code == HTTPStatus.FOUND
    comment.refresh_from_db()
    assert comment.text == new_text


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(
    client,
    reader,
    comment,
    comment_urls
):
    client.force_login(reader)
    response = client.post(
        comment_urls['edit'],
        data={'text': 'Попытка изменить'}
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == 'Комментарий'
