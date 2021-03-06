#!/usr/bin/python
# -*- coding: utf-8 -*-
from UserDict import UserDict
from anki.notes import Note
from pubsub.util import *
from aqt import mw


class AnkipubSubNote(UserDict):
    def __init__(self, note, col=None):
        if isinstance(note, Note):
            UserDict.__init__(self)
            #NoteID Mapping
            self.update({'localID': note.id})
            remoteNoteID = getRemoteNoteID(note.id)
            if remoteNoteID:
                self.update({'id': remoteNoteID})

            #ModelID Mapping
            remoteModelID = getRemoteModelID(note.mid)
            if remoteModelID:
                self.update({'modelID': remoteModelID})
            self.update({'localModelID': note.mid})

            fields = {}
            for key in note.keys():
                fields.update({key: note.values()[note.keys().index(key)]})
            self.update({'fields': fields})
        else:
            UserDict.__init__(self)
            self.update(note.items())

    def setID(self, cardID):
        self.update({'id':  cardID})

    def setLocalID(self, localCardID):
        self.update({'localID':  localCardID})

    def getRemoteID(self):
        return self.get('id')

    def getLocalID(self):
        return self.get('localID')

    def getCreationID(self):
        return self.get('creationCard')

    def getFields(self):
        return self.get('fields')

    def getOldCardID(self):
        return self.get('oldCard')

    def getCreationDate(self):
        return self.get('creationDate')

    def save(self, remoteDeckID):
        col = mw.col
        model = col.models.get(getLocalModelID(self.get('model')))


        if not self.get('localID') and not getLocalNoteID(self.get('creationNote')):
        # Wurde nicht gerade eben gepusht und ist nicht in der Lokalen Datenbank also neu
            note = Note(col, model)
            fields = self.getFields()
            for key in fields:
                note.__setitem__(str(key), fields.get(key))
            note.flush()
            col.addNote(note)
            col.save()
            localID = note.id

        elif self.get('localID')  and not getLocalNoteID(self.get('creationNote')):        # Hat ne lokale Id wurde also eben gepusht aber ist nicht in der Lokalen Datenbank also update
            # Hier muss noch die remoteID in die datenbank geschrieben werden
            localID = self.get('localID')

            print("DO i really need this")
        else:  # Hat nichts von allem also existiert schon also update
            # get remote id for local
            localID = getLocalNoteID(self.get('creationNote'))
            oldNote = Note(col, None, localID)
            fields = self.getFields()
            print('test1')
            for key in fields:
                print('test2')
                if key not in oldNote.keys():
                    print("we changed quite a bit")
                else:
                    print("test3")
                    print(fields.get(key))
                    print(oldNote.__getitem__(key))
                    if not fields.get(key) == oldNote.__getitem__(key):
                        oldNote.__setitem__(key, fields.get(key))
                        oldNote.flush()
                        col.save()
                        print("we changed it")
                    # if fields.get(key) == 
            #print(oldNote.values())
            #print(oldNote.cards())
        col.genCards([localID])
        col.save()
        mw.col.db.execute("INSERT OR REPLACE INTO NoteIDs (RemoteID, RemoteDeckID, LocalID) VALUES (?,?,?)", self.get('creationNote'), remoteDeckID, localID)
