from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note

User = get_user_model()

HOME_URL = reverse('notes:home')
ADD_URL = reverse('notes:add')
LIST_URL = reverse('notes:list')
SUCCESS_URL = reverse('notes:success')
LOGIN_URL = reverse('users:login')
LOGOUT_URL = reverse('users:logout')
SIGNUP_URL = reverse('users:signup')

NOTES_COUNT = 6
NOTE_TEXT = 'Текст заметки'
NEW_NOTE_TEXT = 'Обновлённый текст'
CREATED_NOTE_SLUG = 'created-note'
CREATED_NOTE_TITLE = 'Созданная заметка'
ANON_NOTE_TITLE = 'Новая заметка'
ANON_NOTE_TEXT = 'Текст'


class NotesTestBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(username='Автор')
        cls.reader = User.objects.create_user(username='Читатель')
        cls.author_client = Client()
        cls.reader_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client.force_login(cls.reader)

        cls.notes = []
        for i in range(NOTES_COUNT):
            note = Note.objects.create(
                title=f'Заметка {i}',
                text='Текст',
                slug=f'note-{i}',
                author=cls.author
            )
            cls.notes.append(note)

        cls.note = cls.notes[0]
        cls.detail_url = reverse('notes:detail', args=(cls.note.slug,))
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.list_url = LIST_URL
        cls.create_url = ADD_URL
