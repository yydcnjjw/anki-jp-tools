# -*- coding: utf-8 -*-

import json

import urllib.request

from anki_api import AnkiApi

base_1_url = "http://localhost:8765"
base_2_url = "http://47.101.146.156:8765"

class AnkiConnectApi(AnkiApi):
    __base_url = base_1_url

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            self.__getVersion()
        except Exception:
            AnkiConnectApi.__base_url = base_2_url
            self.__getVersion()

    def addNote(self, deck, model, field, tags):
        return self.__anki_invoke('addNote',
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
        return self.__anki_invoke('canAddNotes',
                                  notes=[{
                                      'deckName': deck,
                                      'modelName': model,
                                      'fields': field,
                                      'tags': tags
                                  }])[0]

    def __getVersion(self):
        return self.__anki_invoke('version')

    def __anki_request(self, action, **params):
        return {'action': action, 'params': params, 'version': 6}

    def __anki_invoke(self, action, **params):
        requestJson = json.dumps(self.__anki_request(
            action, **params)).encode('utf-8')
        response = json.load(
            urllib.request.urlopen(
                urllib.request.Request(self.__base_url, data=requestJson)))
        if len(response) != 2:
            raise Exception('response has an unexpected number of fields')
        if 'error' not in response:
            raise Exception('response is missing required error field')
        if 'result' not in response:
            raise Exception('response is missing required result field')
        if response['error'] is not None:
            raise Exception(response['error'])
        return response['result']
