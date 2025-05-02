from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note

User = get_user_model()


class TestNotesListPage(TestCase):
    HOME_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        notes = [
            Note(
                title=f'Заметка {i}',
                text='Текст',
                slug=f'note-{i}',
                author=cls.author if i % 2 == 0 else cls.reader
            )
            for i in range(11)
        ]
        Note.objects.bulk_create(notes)

    def test_notes_are_displayed(self):
        self.client.force_login(self.author)
        response = self.client.get(self.HOME_URL)
        object_list = response.context['object_list']
        self.assertEqual(len(object_list), 6)

    def test_only_author_notes_are_displayed(self):
        self.client.force_login(self.author)
        response = self.client.get(self.HOME_URL)
        object_list = response.context['object_list']
        self.assertTrue(
            all(note.author == self.author for note in object_list)
        )

    def test_another_user_notes_not_in_list(self):
        self.client.force_login(self.reader)
        response = self.client.get(self.HOME_URL)
        object_list = response.context['object_list']
        self.assertTrue(
            all(note.author == self.reader for note in object_list)
        )


class TestNoteDetailPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.note = Note.objects.create(
            title='Тестовая заметка',
            text='Текст заметки',
            slug='test-note',
            author=cls.author
        )
        cls.detail_url = reverse('notes:detail', args=(cls.note.slug,))

    def test_note_detail_page(self):
        self.client.force_login(self.author)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.context['note'], self.note)


class TestNoteCreatePage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.create_url = reverse('notes:add')

    def test_note_create_page(self):
        self.client.force_login(self.author)
        response = self.client.get(self.create_url)
        self.assertContains(response, '<form')
        self.assertContains(response, 'name="title"')
        self.assertContains(response, 'name="text"')


class TestNoteEditPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.note = Note.objects.create(
            title='Тестовая заметка',
            text='Текст заметки',
            slug='test-note',
            author=cls.author
        )
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))

    def test_note_edit_page(self):
        self.client.force_login(self.author)
        response = self.client.get(self.edit_url)
        self.assertContains(response, '<form')
        self.assertContains(response, f'value="{self.note.title}"')
