#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json

import colorful

from api.anki_api import \
    AnkiApi, \
    format_descs, \
    format_simple

from hjdict import \
    HJDictService, \
    format_hjdict, \
    MultiWordsException,\
    NotfoundException


def print_bold(s):
    print(colorful.bold | s)


def handle_multiwords(check_word, multi_words, dict_service):
    print_bold('Multi words:')
    for i, word in enumerate(multi_words):
        print_bold("%d: %s %s" %
                   (i, word.get('expression', ''), word.get('pronounce', '')))
    number = 0
    try:
        number = int(input('Input Number: '))
    except ValueError:
        print(colorful.red | "Error input !")
        handle_multiwords(check_word, multi_words, dict_service)

    if len(multi_words) > number:
        expression = multi_words[number].get('expression', '')
        pronounce = multi_words[number].get('pronounce', '')
        word_dict = dict_service.get_dict(expression, pronounce)
        expression = word_dict.get('word_expressions', '')
        pronounce = word_dict.get('word_pronounce', '')
        if check_word == expression:
            word_dict['word_expressions'] = expression + pronounce

        print(colorful.bold | format_hjdict(word_dict))
        save(word_dict)
    else:
        print(colorful.red | "Error input!")


def save(word_dict):
    confirm = input('save to anki[y/N]: ')
    if confirm == 'y':
        word_simple = word_dict.get('word_simple', [])
        word_descs = word_dict.get('word_descs', [])
        word_simple_null = len(word_simple) == 0
        if word_simple_null:
            word_simple = word_descs

        audio_url = word_dict.get('word_audio', '')
        if audio_url.startswith('https://'):
            audio_url = audio_url.replace('https://', 'http://', 1)

        field = {
            'expression':
            word_dict.get('word_expressions', ''),
            'pronounce':
            word_dict.get('word_pronounce', ''),
            'kata':
            word_dict.get('word_kata', ''),
            'tone':
            word_dict.get('word_tone', ''),
            'audio':
            "[sound:%s]" % audio_url,
            'simple':
            format_simple(word_simple, word_simple_null),
            'sentence':
            format_descs(word_dict.get('word_descs', []))
        }

        tags = ['japanese(dict)']
        model = 'japanese(dict)'
        deck = 'Japanese_Word'
        anki_api = AnkiApi.getApi('anki_connect')
        if anki_api.canAddNote(deck, model, field, tags):
            print(anki_api.addNote(deck, model, field, tags))
            # TODO: save
            # file = open(
            #     '/home/yydcnjjw/workspace/code/project/'
            #     'anki-jp-tools/save_dict', 'a')
            # file.write(json.dumps(word_dict) + "\n")
            # file.close()
        else:
            print(colorful.bold & colorful.red
                  | 'Can not add note ! Duplicate !')
    else:
        print("Disable!")


DEBUG = False


def printException(e):
    if DEBUG:
        raise e
    else:
        print(colorful.red | e)


def main():
    dict_service = HJDictService()
    check_word = ""
    try:
        word_dict = ""
        if len(sys.argv) == 2:
            check_word = sys.argv[1]
            word_dict = dict_service.get_dict(sys.argv[1])

        print(colorful.bold | format_hjdict(word_dict))
        save(word_dict)

    except MultiWordsException as e:
        try:
            handle_multiwords(check_word, e.multi_words, dict_service)
        except Exception as e:
            printException(e)
    except NotfoundException as e:
        print(colorful.bold & colorful.red | e)
    except Exception as e:
        printException(e)
        # raise e


main()
