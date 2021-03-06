# -*- coding: utf-8 -*-

import re

import urllib.request
import colorful
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

css_word_simple = ('header.word-details-pane-header > ' 'div.simple')

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
    def __init__(self, multi_words):
        self.multi_words = multi_words


class HJDictApi:
    def __init__(self):
        self.soup = None
        self.expression = ''

    def get_dict(self, expression, pronounce=None):
        if expression != self.expression:
            self.expression = expression
            request = urllib.request.Request(
                "%s%s" % (api_url, urllib.request.quote(expression)),
                headers={
                    "User-Agent": useragent,
                    "Cookie": Cookie
                })
            result = urllib.request.urlopen(request, timeout=10).read()
            self.soup = BeautifulSoup(result, 'html.parser')

        soup = self.soup

        if self._not_found(soup):
            raise NotfoundException("Not Found word")

        multi_words = self._get_multi_words(soup, expression)
        if multi_words is not None:
            if pronounce is None:
                raise MultiWordsException(multi_words)

        word_blocks = self._get_word_block(soup)
        if word_blocks is None:
            raise NotfoundException("Html format error")

        for block in word_blocks:
            if block.get('expression', '') == expression and block.get(
                    'pronounce', '') == pronounce:
                soup = block.get('block', '')

        return self._get_dict_result(soup)

    def _get_word_block(self, soup):
        word_blocks = soup.select(css_word_block)
        if word_blocks is None:
            return None
        block_list = []
        for word_block in word_blocks:
            expression = self._get_format_string(
                word_block.select(css_word_text)[0])
            pronounce = self._get_format_string(
                word_block.select(css_word_pronounces)[0])
            block_list.append({
                'block': word_block,
                'expression': expression,
                'pronounce': pronounce
            })
        return block_list

    def _not_found(self, soup):
        return soup.select(css_notfound) or soup.select(css_word_suggestions)

    def _get_multi_words(self, soup, word):
        multi_words = soup.select(css_multi_word)
        word_list = []
        if multi_words and len(multi_words) != 0:
            for word in multi_words:
                expression = self._get_format_string(word.h2)
                pronounce = self._get_format_string(word.div.span)
                word_list.append({
                    'expression': expression,
                    'pronounce': pronounce
                })
            return word_list
        else:
            return None

    def _get_dict_result(self, soup):
        word_expressions = self._get_format_string(
            soup.select_one(css_word_text))
        word_pronounces = soup.select(css_word_pronounces)
        if word_expressions is None:
            raise NotfoundException("Html format error")

        word_pronounce = ""
        word_kata = ""
        word_tone = ""
        word_audio = ""
        for i, word_reading in enumerate(word_pronounces):
            if i == 0:
                word_pronounce = self._get_format_string(word_reading)
            elif word_reading.get('data-src', None) and word_reading.get(
                    'class', None):
                word_audio = word_reading['data-src']
            elif word_reading.get('class', None):
                word_tone = self._get_format_string(word_reading)
            else:
                word_kata = self._get_format_string(word_reading)

        word_simple_block = soup.select(css_word_simple)
        if word_simple_block is None:
            raise NotfoundException("Html format error")

        # [{type
        #   [mean]}]
        word_simple = []
        for word_simples in word_simple_block:
            word_simple_types = word_simples.findAll('h2')
            word_simple_details_list = word_simples.findAll('ul')

            for i in range(len(word_simple_details_list)):
                simple_type = self._get_format_string(
                    word_simple_types[i]) if i < len(word_simple_types) else ''
                simple_details = []
                simple_detail_list = word_simple_details_list[i].findAll('li')
                for detail in simple_detail_list:
                    if re.match(r'\d+\.', detail.span.string):
                        detail.span.clear()
                    simple_details.append(self._get_format_string(detail))
                word_simple.append({
                    'simple_type': simple_type,
                    'simple_details': simple_details
                })

        word_desc_lists = soup.select(css_word_details_list)
        if word_desc_lists is None:
            raise NotfoundException("Html format error")

        # [{type
        #   [jp mean
        #   cn mean
        #   [sentence]]}]
        word_descs = []

        for word_desc in word_desc_lists:
            word_type = self._get_format_string(word_desc.find("dt"))
            word_means = word_desc.findAll("dd")
            meanings = []
            for mean in word_means:
                details = mean.find("h3")
                if details is None:
                    continue
                details = details.findAll("p")
                if len(details) < 2:
                    continue
                jp_mean = self._get_format_string(details[0])
                cn_mean = self._get_format_string(details[1])
                if len(jp_mean) == 0 and len(cn_mean) == 0:
                    continue
                sentences = []
                sentences_list = mean.findAll("li")
                for sentence in sentences_list:
                    sentence_desc = sentence.findAll("p")
                    if len(sentence_desc) != 2:
                        continue
                    sentence_jp_block = sentence_desc[0]
                    sentence_jp = self._get_format_string(sentence_jp_block)
                    sentence_audio = sentence_jp_block.span["data-src"]
                    sentence_cn = self._get_format_string(sentence_desc[1])
                    sentences.append({
                        'sentence_jp': sentence_jp,
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
            'word_simple': word_simple,
            'word_descs': word_descs
        }

    def _get_format_string(self, s):
        if s and s.string is None:
            ret = ""
            for string in s.stripped_strings:
                ret += string
            return ret
        else:
            return s.string.strip()
