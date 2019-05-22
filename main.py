#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json

import colorful

from anki_api import \
    anki_addNote, \
    anki_canAddNote, \
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
        if anki_canAddNote(word_dict):
            print(anki_addNote(word_dict))

            # TODO: save
            file = open(
                '/home/yydcnjjw/workspace/code/project/'
                'anki-jp-tools/save_dict', 'a')
            file.write(json.dumps(word_dict) + "\n")
            file.close()
        else:
            print(colorful.bold & colorful.red
                  | 'Can not add note ! Duplicate !')
    else:
        print("Disable!")


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
            raise e
    except NotfoundException as e:
        print(colorful.bold & colorful.red | e)
    except Exception as e:
        raise e


main()
