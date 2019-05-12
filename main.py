#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json

import urllib.request

from bs4 import BeautifulSoup

css_notfound = 'div.word-notfound-inner'
css_word_suggestions = 'div.word-suggestions'
css_multi_word = 'header.word-details-header > ul > li'
css_word_block = ('section.word-details-content > ' 'div.word-details-pane')
css_word_text = ('header.word-details-pane-header > '
                 'div.word-info > '
                 'div.word-text > '
                 'h2')
css_word_pronounces = ('header.word-details-pane-header > '
                       'div.word-info > '
                       'div.pronounces > '
                       'span')

css_word_details_list = ('div.word-details-item-content > '
                         'section.detail-groups > '
                         'dl')

useragent = ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
             '(KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36')
Cookie = 'HJ_UID=0f406091-be97-6b64-f1fc-f7b2470883e9; HJ_CST=1; HJ_CSST_3=1;\
TRACKSITEMAP=3%2C; HJ_SID=393c85c7-abac-f408-6a32-a1f125d7e8c6; _REF=; \
HJ_SSID_3=4a460f19-c0ae-12a7-8e86-6e360f69ec9b; _SREF_3=; HJ_CMATCH=1'

api_url = 'http://www.hjdict.com/jp/jc/'


class NotfoundException(Exception):
    pass


class MultiWordsException(Exception):
    pass


class HJDictService:
    def get_dict(self, expression, pronounce=None):
        request = urllib.request.Request(
            "%s%s" % (api_url, urllib.request.quote(expression)),
            headers={
                "User-Agent": useragent,
                "Cookie": Cookie
            })
        result = urllib.request.urlopen(request, timeout=10).read()
        soup = BeautifulSoup(result, 'html.parser')

        if self.not_found(soup):
            raise NotfoundException("Not Found word")

        multi_words = self.get_multi_words(soup)
        if multi_words is not None:
            if pronounce is None:
                text = "\n"
                for word in multi_words:
                    text += "%s %s\n" % (word.get(
                        'expression', ''), word.get('pronounce', ''))
                raise MultiWordsException("Multi words", text)

        word_blocks = self.get_word_block(soup)
        for block in word_blocks:
            if block.get('expression', '') == expression and block.get(
                    'pronounce', '') == pronounce:
                soup = block.get('block', '')

        return self.get_dict_result(soup)

    def get_word_block(self, soup):
        word_blocks = soup.select(css_word_block)
        block_list = []
        for word_block in word_blocks:
            expression = self.get_format_string(
                word_block.select(css_word_text)[0])
            pronounce = self.get_format_string(
                word_block.select(css_word_pronounces)[0])
            block_list.append({
                'block': word_block,
                'expression': expression,
                'pronounce': pronounce
            })
        return block_list

    def not_found(self, soup):
        return len(soup.select(css_notfound)) != 0 or len(
            soup.select(css_word_suggestions))

    def get_multi_words(self, soup):
        multi_words = soup.select(css_multi_word)
        word_list = []
        if len(multi_words) != 0:
            for word in multi_words:
                expression = self.get_format_string(word.h2)
                pronounce = self.get_format_string(word.div.span)
                word_list.append({
                    'expression': expression,
                    'pronounce': pronounce
                })
            return word_list
        else:
            return None

    def get_dict_result(self, soup):
        word_expressions = self.get_format_string(
            soup.select(css_word_text)[0])
        word_pronounces = soup.select(css_word_pronounces)
        word_pronounce = ""
        word_kata = ""
        word_tone = ""
        word_audio = ""
        for i, word_reading in enumerate(word_pronounces):
            if i == 0:
                word_pronounce = self.get_format_string(word_reading)
            elif word_reading.get('data-src', None) and word_reading.get(
                    'class', None):
                word_audio = word_reading['data-src']
            elif word_reading.get('class', None):
                word_tone = self.get_format_string(word_reading)
            else:
                word_kata = self.get_format_string(word_reading)

        word_desc_lists = soup.select(css_word_details_list)
        # [{type
        #   [jp mean
        #   cn mean
        #   [sentence]]}]
        word_descs = []

        for word_desc in word_desc_lists:
            word_type = word_desc.findChildren("dt")[0].string.strip()
            word_means = word_desc.findChildren("dd")
            meanings = []
            for mean in word_means:
                details = mean.findChildren("h3")[0].findChildren("p")
                jp_mean = self.get_format_string(details[0])
                cn_mean = self.get_format_string(details[1])
                sentences = []
                sentences_list = mean.findChildren("ul")[0].findChildren("li")
                for sentence in sentences_list:
                    sentence_desc = sentence.findChildren("p")
                    sentence_jp_block = sentence_desc[0]
                    sentence_jp = sentence_jp_block.stripped_strings
                    sentence_jp_str = ""
                    for s in sentence_jp:
                        sentence_jp_str += s
                    sentence_audio = sentence_jp_block.span["data-src"]
                    sentence_cn = sentence_desc[1].string.strip()
                    sentences.append({
                        'sentence_jp': sentence_jp_str,
                        'sentence_cn': sentence_cn,
                        'sentence_audio': sentence_audio
                    })
                meanings.append({
                    'jp_mean': jp_mean,
                    'cn_mean': cn_mean,
                    'sentences': sentences
                })

            word_descs.append({'word_type': word_type, 'meanings': meanings})

        return {
            'word_expressions': word_expressions,
            'word_pronounce': word_pronounce,
            'word_kata': word_kata,
            'word_tone': word_tone,
            'word_audio': word_audio,
            'word_descs': word_descs
        }

    def get_format_string(self, s):
        if s.string is None:
            return ''
        else:
            return s.string.strip()


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
                           'deckName': 'Test',
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
                               word_dict.get('word_audio', ''),
                               'simple':
                               format_simple(word_dict.get('word_descs', [])),
                               'sentence':
                               format_descs(word_dict.get('word_descs', []))
                           },
                           'tags': ['anki_test'],
                           'options': {
                               'allowDuplicate': True
                           }
                       })


def main():
    try:
        word_dict = ""
        if len(sys.argv) == 2:
            word_dict = HJDictService().get_dict(sys.argv[1])
        elif len(sys.argv) == 3:
            word_dict = HJDictService().get_dict(sys.argv[1], sys.argv[2])
        # card_id = anki_addNote(word_dict)
        print(word_dict)
    except Exception as e:
        raise e
        # print(e)


main()
