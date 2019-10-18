# -*- coding: utf-8 -*-

import json

import urllib.request

from anki_api import AnkiApi


class AnkiConnectApi(AnkiApi):
    def addNote(self, deck, model, field, tags):
        return anki_invoke('addNote',
                           note={
                               'deckName': deck,
                               'modelName': model,
                               'fields': field,
                               'tags': tags,
                               'options': {
                                   'allowDuplicate': False
                               }
                           })

    def canAddNote(self, deck, model, field, tags):
        return anki_invoke('canAddNotes',
                           notes=[{
                               'deckName': deck,
                               'modelName': model,
                               'fields': field,
                               'tags': tags
                           }])[0]

    @staticmethod
    def __getVersion():
        return anki_invoke('version', version=6)

    @staticmethod
    def tryConnect():
        try:
            AnkiConnectApi.__getVersion()
            return True
        except Exception:
            return False


def __anki_request(self, action, **params):
    return {'action': action, 'params': params, 'version': 6}


def anki_invoke(action, **params):
    requestJson = json.dumps(__anki_request(action, **params)).encode('utf-8')
    response = json.load(
        urllib.request.urlopen(
            urllib.request.Request('http://localhost:8765', data=requestJson)))
    if len(response) != 2:
        raise Exception('response has an unexpected number of fields')
    if 'error' not in response:
        raise Exception('response is missing required error field')
    if 'result' not in response:
        raise Exception('response is missing required result field')
    if response['error'] is not None:
        raise Exception(response['error'])
    return response['result']
