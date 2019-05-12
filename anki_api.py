# -*- coding: utf-8 -*-

import json

import urllib.request


def format_simple(descs):
    result = ""
    result += """<dl>"""
    for desc in descs:
        word_type = desc.get('word_type')
        result += """<dt>%s</dt>""" % word_type
        result += """<dd>"""
        result += """<ul>"""
        word_meanings = desc.get('meanings')
        for mean in word_meanings:
            cn_mean = mean.get('cn_mean')
            result += """<li><span>%s</span></li>""" % cn_mean
        result += """<ul>"""
        result += """</dd>"""
    result += """</dl>"""
    return result


def format_descs(descs):
    result = ""
    result += """<dl>"""
    for desc in descs:
        word_type = desc.get('word_type')
        result += """<dt>%s</dt>""" % word_type
        result += """<dd>"""
        result += """<ul>"""
        word_meanings = desc.get('meanings')
        for mean in word_meanings:
            jp_mean = mean.get('jp_mean')
            cn_mean = mean.get('cn_mean')
            result += "<li>"
            result += """<span>%s</span>/<span>%s</span>""" % (cn_mean,
                                                               jp_mean)

            result += """<ul>"""
            sentences = mean.get('sentences')
            for sentence in sentences:
                result += """<li>"""
                sentence_jp = sentence.get('sentence_jp')
                sentence_cn = sentence.get('sentence_cn')
                sentence_audio = sentence.get('sentence_audio')
                result += "%s \\ %s [sound:%s]" % (sentence_jp, sentence_cn,
                                                   sentence_audio)
                result += """</li>"""
            result += """</ul>"""
            result += "</li>"
        result += """</ul>"""
        result += """</dd>"""
    result += """</dl>"""
    return result


def anki_request(action, **params):
    return {'action': action, 'params': params, 'version': 6}


def anki_invoke(action, **params):
    requestJson = json.dumps(anki_request(action, **params)).encode('utf-8')
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


def anki_addNote(word_dict):
    return anki_invoke('addNote',
                       note={
                           'deckName': 'Japanese_Wrod',
                           'modelName': 'japanese(dict)',
                           'fields': {
                               'expression':
                               word_dict.get('word_expressions', ''),
                               'pronounce':
                               word_dict.get('word_pronounce', ''),
                               'kata':
                               word_dict.get('word_kata', ''),
                               'tone':
                               word_dict.get('word_tone', ''),
                               'audio':
                               "[sound:%s]" % word_dict.get('word_audio', ''),
                               'simple':
                               format_simple(word_dict.get('word_descs', [])),
                               'sentence':
                               format_descs(word_dict.get('word_descs', []))
                           },
                           'tags': ['japanese(dict)'],
                           'options': {
                               'allowDuplicate': False
                           }
                       })


def anki_canAddNote(word_dict):
    return anki_invoke('canAddNotes',
                       notes=[{
                           'deckName': 'Japanese_Wrod',
                           'modelName': 'japanese(dict)',
                           'fields': {
                               'expression':
                               word_dict.get('word_expressions', ''),
                               'pronounce':
                               word_dict.get('word_pronounce', '')
                           },
                           'tags': ['japanese(dict)']
                       }])[0]
