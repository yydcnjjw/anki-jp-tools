# -*- coding: utf-8 -*-

import json

import urllib.request


def format_simple(simples, is_descs=False):
    result = ""
    if is_descs:
        descs = simples
        result += """<dl>"""
        for desc in descs:
            word_type = desc.get('word_type', '')
            result += """<dt>%s</dt>""" % word_type
            result += """<dd>"""
            result += """<ul>"""
            word_meanings = desc.get('meanings', [])
            for mean in word_meanings:
                cn_mean = mean.get('cn_mean', '')
                result += "<li>"
                result += """<span>%s</span>""" % cn_mean
                result += "</li>"
            result += """</ul>"""
            result += """</dd>"""
        result += """</dl>"""
    else:
        result += """<dl>"""
        for desc in simples:
            word_type = desc.get('simple_type', '')
            result += """<dt>%s</dt>""" % word_type
            result += """<dd>"""
            result += """<ul>"""
            word_details = desc.get('simple_details', [])
            for detail in word_details:
                result += """<li><span>%s</span></li>""" % detail
            result += """<ul>"""
            result += """</dd>"""
        result += """</dl>"""
    return result


def format_descs(descs):
    result = ""
    result += """<dl>"""
    for desc in descs:
        word_type = desc.get('word_type', '')
        result += """<dt>%s</dt>""" % word_type
        result += """<dd>"""
        result += """<ul>"""
        word_meanings = desc.get('meanings', [])
        for mean in word_meanings:
            jp_mean = mean.get('jp_mean', '')
            cn_mean = mean.get('cn_mean', '')
            result += "<li>"
            result += """<span>%s</span>/<span>%s</span>""" % (cn_mean,
                                                               jp_mean)

            result += """<ul>"""
            sentences = mean.get('sentences', [])
            for sentence in sentences:
                result += """<li>"""
                sentence_jp = sentence.get('sentence_jp', '')
                sentence_cn = sentence.get('sentence_cn', '')
                sentence_audio = sentence.get('sentence_audio')
                if sentence_audio.startswith('https://'):
                    sentence_audio = sentence_audio.replace('https://', 'http://', 1)
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


def anki_addNote(deck, model, field, tags):
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


def anki_canAddNote(deck, model, field, tags):
    return anki_invoke('canAddNotes',
                       notes=[{
                           'deckName': deck,
                           'modelName': model,
                           'fields': field,
                           'tags': tags
                       }])[0]
