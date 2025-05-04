import pytest
from http import HTTPStatus

from django.urls import reverse
from django.contrib.auth import get_user_model

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

User = get_user_model()


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news):
    url = reverse('news:detail', args=(news.id,))
    comments_before = Comment.objects.count()
    client.post(url, data={'text': 'Анонимный комментарий'})
    comments_after = Comment.objects.count()
    assert comments_after == comments_before


@pytest.mark.django_db
def test_user_can_create_comment(author_client, author, news):
    url = reverse('news:detail', args=(news.id,))
    comments_before = Comment.objects.count()
    response = author_client.post(url, data={'text': 'Тестовый комментарий'})
    comments_after = Comment.objects.count()
    assert response.status_code == HTTPStatus.FOUND
    assert comments_after == comments_before + 1
    comment = Comment.objects.get(author=author, text='Тестовый комментарий')
    assert comment.news == news


@pytest.mark.django_db
def test_user_cant_use_bad_words(author_client, news):
    url = reverse('news:detail', args=(news.id,))
    comments_before = Comment.objects.count()
    response = author_client.post(
        url,
        data={'text': f'Плохое слово {BAD_WORDS[0]}'}
    )
    response.render()
    form = response.context['form']
    comments_after = Comment.objects.count()
    assert form.errors['text'][0] == WARNING
    assert comments_after == comments_before


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, comment, comment_urls):
    comments_before = Comment.objects.count()
    response = author_client.delete(comment_urls['delete'])
    comments_after = Comment.objects.count()
    assert response.status_code == HTTPStatus.FOUND
    assert comments_after == comments_before - 1
    assert not Comment.objects.filter(id=comment.id).exists()


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(
    reader_client,
    comment,
    comment_urls
):
    comments_before = Comment.objects.count()
    response = reader_client.delete(comment_urls['delete'])
    comments_after = Comment.objects.count()
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert comments_after == comments_before
    assert Comment.objects.filter(id=comment.id).exists()


@pytest.mark.django_db
def test_author_can_edit_comment(author_client, comment, comment_urls):
    new_text = 'Обновлённый текст'
    response = author_client.post(
        comment_urls['edit'],
        data={'text': new_text}
    )
    assert response.status_code == HTTPStatus.FOUND
    comment.refresh_from_db()
    assert comment.text == new_text


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(
    reader_client,
    comment,
    comment_urls
):
    response = reader_client.post(
        comment_urls['edit'],
        data={'text': 'Попытка изменить'}
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == 'Комментарий'
