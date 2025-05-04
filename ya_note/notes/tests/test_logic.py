from http import HTTPStatus

from django.db import IntegrityError
from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from pytils.translit import slugify

from notes.models import Note


User = get_user_model()


class TestNoteAccessLogic(TestCase):
    NOTE_TEXT = 'Текст заметки'
    NEW_NOTE_TEXT = 'Обновлённый текст'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')

        cls.author_client = Client()
        cls.reader_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client.force_login(cls.reader)

        cls.note = Note.objects.create(
            title='Заметка',
            text=cls.NOTE_TEXT,
            slug='test-note',
            author=cls.author
        )

        cls.detail_url = reverse('notes:detail', args=(cls.note.slug,))
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.success_url = reverse('notes:success')
        cls.form_data = {
            'title': cls.note.title,
            'text': cls.NEW_NOTE_TEXT,
            'slug': cls.note.slug
        }

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)

    def test_reader_cant_edit_note(self):
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT)

    def test_author_can_delete_note(self):
        notes_before = Note.objects.count()
        response = self.author_client.post(self.delete_url)
        notes_after = Note.objects.count()
        self.assertRedirects(response, self.success_url)
        self.assertEqual(notes_after, notes_before - 1)
        self.assertFalse(Note.objects.filter(pk=self.note.pk).exists())

    def test_reader_cant_delete_note(self):
        notes_before = Note.objects.count()
        response = self.reader_client.post(self.delete_url)
        notes_after = Note.objects.count()
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(notes_after, notes_before)
        self.assertTrue(Note.objects.filter(pk=self.note.pk).exists())

    def test_author_can_create_note(self):
        url = reverse('notes:add')
        notes_before = Note.objects.count()
        data = {
            'title': 'Созданная заметка',
            'text': 'Текст созданной заметки',
            'slug': 'created-note'
        }
        response = self.author_client.post(url, data=data)
        notes_after = Note.objects.count()
        self.assertRedirects(response, self.success_url)
        self.assertEqual(notes_after, notes_before + 1)
        self.assertTrue(Note.objects.filter(slug='created-note').exists())

    def test_anonymous_cant_create_note(self):
        url = reverse('notes:add')
        response = self.client.post(
            url,
            data={'title': 'Новая заметка', 'text': 'Текст'}
        )
        login_url = reverse('users:login')
        redirect_url = f'{login_url}?next={url}'
        self.assertRedirects(response, redirect_url)

    def test_unique_slug_validation(self):
        Note.objects.create(
            title='Первая заметка',
            text='Текст первой заметки',
            slug='unique-slug',
            author=self.author
        )
        with self.assertRaises(IntegrityError):
            Note.objects.create(
                title='Дубликат заметки',
                text='Текст дубликата',
                slug='unique-slug',
                author=self.author
            )

    def test_slug_is_automatically_generated(self):
        url = reverse('notes:add')
        data = {'title': 'Новая заметка', 'text': 'Текст новой заметки'}
        response = self.author_client.post(url, data=data)
        self.assertRedirects(response, self.success_url)
        note = Note.objects.get(title='Новая заметка')
        expected_slug = slugify('Новая заметка')
        self.assertEqual(note.slug, expected_slug)
