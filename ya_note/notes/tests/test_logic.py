from http import HTTPStatus

from django.db import IntegrityError
from django.urls import reverse
from pytils.translit import slugify

from notes.models import Note
from .common import (
    NotesTestBase,
    ADD_URL,
    SUCCESS_URL,
    NOTE_TEXT,
    NEW_NOTE_TEXT,
    CREATED_NOTE_SLUG,
    CREATED_NOTE_TITLE,
    ANON_NOTE_TITLE,
    ANON_NOTE_TEXT
)


class TestNoteAccessLogic(NotesTestBase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.note.text = NOTE_TEXT
        cls.note.save()
        cls.success_url = SUCCESS_URL
        cls.form_data = {
            'title': cls.note.title,
            'text': NEW_NOTE_TEXT,
            'slug': cls.note.slug
        }

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, NEW_NOTE_TEXT)

    def test_reader_cant_edit_note(self):
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, NOTE_TEXT)

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
        notes_before = Note.objects.count()
        data = {
            'title': CREATED_NOTE_TITLE,
            'text': 'Текст созданной заметки',
            'slug': CREATED_NOTE_SLUG
        }
        response = self.author_client.post(ADD_URL, data=data)
        notes_after = Note.objects.count()
        self.assertRedirects(response, self.success_url)
        self.assertEqual(notes_after, notes_before + 1)
        self.assertTrue(Note.objects.filter(slug=CREATED_NOTE_SLUG).exists())

    def test_anonymous_cant_create_note(self):
        response = self.client.post(
            ADD_URL,
            data={'title': ANON_NOTE_TITLE, 'text': ANON_NOTE_TEXT}
        )
        login_url = reverse('users:login')
        redirect_url = f'{login_url}?next={ADD_URL}'
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
        data = {'title': ANON_NOTE_TITLE, 'text': 'Текст новой заметки'}
        response = self.author_client.post(ADD_URL, data=data)
        self.assertRedirects(response, self.success_url)
        note = Note.objects.get(title=ANON_NOTE_TITLE)
        expected_slug = slugify(ANON_NOTE_TITLE)
        self.assertEqual(note.slug, expected_slug)
