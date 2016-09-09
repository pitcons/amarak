# encoding: utf8
from .note import Note


class NotesManager(object):

    def __init__(self):
        self._notes = []
        self._changes = []

    def _add_raw(self, lang, note_type, literal, id=None):
        note = Note(lang, note_type, literal, id=id)
        self._notes.append(note)
        return note

    def add(self, lang, note_type, literal, id=None):
        note = self._add_raw(lang, note_type, literal, id)
        self._changes.append(('new', note))

    def _remove_raw(self, note):
        self._notes.remove(note)

    def remove(self, note):
        self._remove_raw(note)
        self._changes.append(('remove', note))

    def remove_by_id(self, note_id):
        self._changes.append(('remove_by_id', note_id))

    def all(self):
        return self._notes

    def clear(self):
        for note in self._notes:
            self.remove(note)

    def to_python(self):
        return [
            {'id': note.id,
             'lang': note.lang,
             'type': note.type,
             'literal': note.literal}
            for note in self.all()
        ]
