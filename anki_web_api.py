# -*- coding: utf-8 -*-

import json
import re
from http import cookiejar

from urllib import request
from urllib import parse
from bs4 import BeautifulSoup

from anki_api import AnkiApi


class AnkiWebApi(AnkiApi):
    __cookie_file_name = 'anki_cookie'
    __cookie = cookiejar.FileCookieJar(__cookie_file_name)
    __opener = request.build_opener(request.HTTPCookieProcessor(__cookie))
    __csrf_token = ''
    __models = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__login('yydcnjjw@gmail.com', 'jp52VNe2mFmtXZ4')

    def __login(self, username, pwd):
        # first: login get cookie(ankiweb=login) and csrf_token
        resp = self.__opener.open('https://ankiweb.net/account/login')
        soup = BeautifulSoup(resp, 'html.parser')
        self.__csrf_token = soup.select_one('input[name=csrf_token]')['value']

        form_data = {
            'submitted': '1',
            'username': username,
            'password': pwd,
            'csrf_token': self.__csrf_token
        }

        data = parse.urlencode(form_data).encode('utf-8')

        # second: login set cookie value(ankiweb)
        self.__opener.open('https://ankiweb.net/account/login', data=data)

        # third: handle https://ankiuser.net/edit/ html for get model and deck
        self.__getAnkiUserInfo()

    def __getAnkiUserInfo(self):
        # NOTE: url must be "https://ankiuser.net/edit/"
        resp = self.__opener.open(
            'https://ankiuser.net/edit/').read().decode('utf-8')

        re_models = re.compile(r'editor\.models = (.*}]);')
        model_metas = json.loads(re_models.search(resp).group(1))

        for model in model_metas:
            self.__models[model['name']] = {
                'id': model['id'],
                'fields': list(map(lambda field: field['name'], model['flds']))
            }
        print(self.__models)
        # re_decks = re.compile(r'editor\.decks = (.*}});')
        # deck_metas = json.loads(re_decks.search(resp).group(1))

    def addNote(self, deck, model, fields, tags):
        model_fields = self.__models[model]['fields']
        field_data = [''] * len(model_fields)
        for (field_name, field_value) in fields.items():
            field_data[model_fields.index(field_name)] = field_value
        print(model_fields)
        print(fields)
        print(json.dumps([field_data, tags]).encode('utf-8'))
        form_data = {
            'data': json.dumps([field_data, tags]).encode('utf-8'),
            'csrf_token': self.__csrf_token,
            'mid': self.__models[model]['id'],
            'deck': deck
        }
        data = parse.urlencode(form_data).encode('utf-8')
        print(data)
        resp = self.__opener.open(
            'https://ankiuser.net/edit/save', data=data).read().decode('utf-8')
        print(resp)
        return resp == '1'

    def canAddNote(self, deck, model, field, tags):
        pass

    @staticmethod
    def __getVersion():
        pass

    @staticmethod
    def tryConnect():
        try:
            AnkiWebApi.__getVersion()
            return True
        except Exception:
            return False

# def anki_add_note(deck, model, field):
#     formData = {
#         'csrf_token': csrf_token,
#         'data': field,
#         'mid': model,
#         'deck': deck
#     }

#     response = opener.open('https://ankiuser.net/edit/save', data=formData)
#     return response


if __name__ == "__main__":
    model = '基础'
    deck = 'Test'
    api = AnkiWebApi()
    api.addNote(deck, model, {
        '正面': 'aaaccc',
        '背面': 'bbb'
    }, 'aaaaaa')
    # res = opener.open('https://ankiuser.net/edit/')
