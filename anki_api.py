from abc import abstractmethod


class AnkiApi:
    __instance = None

    @abstractmethod
    def addNote(self, deck, model, field, tags):
        pass

    @abstractmethod
    def canAddNote(self, model, field, tags):
        pass

    @staticmethod
    def getApi(type='auto'):
        from anki_connect_api import AnkiConnectApi
        from anki_web_api import AnkiWebApi
        if AnkiApi.__instance is not None:
            return AnkiApi.__instance
        if type == 'auto':
            return AnkiConnectApi()
        elif type == 'anki_connect':
            return AnkiConnectApi()


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
                    sentence_audio = sentence_audio.replace(
                        'https://', 'http://', 1)
                result += "%s \\ %s [sound:%s]" % (sentence_jp, sentence_cn,
                                                   sentence_audio)
                result += """</li>"""
            result += """</ul>"""
            result += "</li>"
        result += """</ul>"""
        result += """</dd>"""
    result += """</dl>"""
    return result
