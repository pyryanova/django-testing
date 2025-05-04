from notes.forms import NoteForm
from .common import NotesTestBase


class TestNotesListPage(NotesTestBase):
    def test_notes_are_displayed(self):
        response = self.author_client.get(self.list_url)
        object_list = response.context['object_list']
        self.assertEqual(len(object_list), 6)

    def test_only_author_notes_are_displayed(self):
        response = self.author_client.get(self.list_url)
        object_list = response.context['object_list']
        self.assertTrue(
            all(note.author == self.author for note in object_list)
        )

    def test_another_user_notes_not_in_list(self):
        response = self.reader_client.get(self.list_url)
        object_list = response.context['object_list']
        self.assertTrue(
            all(note.author == self.reader for note in object_list)
        )


def test_note_detail_page(self):
    self.author_client.force_login(self.author)
    response = self.author_client.get(self.DETAIL_URL)
    self.assertEqual(response.context['note'].pk, self.note.pk)


class TestNoteCreatePage(NotesTestBase):
    def test_note_create_page(self):
        response = self.author_client.get(self.create_url)
        self.assertContains(response, '<form')
        self.assertContains(response, 'name="title"')
        self.assertContains(response, 'name="text"')
        self.assertIsInstance(response.context['form'], NoteForm)


class TestNoteEditPage(NotesTestBase):
    def test_note_edit_page(self):
        response = self.author_client.get(self.edit_url)
        self.assertContains(response, '<form')
        self.assertContains(response, f'value="{self.note.title}"')
        self.assertIsInstance(response.context['form'], NoteForm)
