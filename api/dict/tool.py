import colorful

def format_hjdict(word_dict):
    result = "%s\n" % word_dict.get('word_expressions', '')
    result += "%s %s %s\n" % (word_dict.get('word_pronounce'),
                              word_dict.get('word_kata', ''),
                              word_dict.get('word_tone', ''))

    word_simple = word_dict.get('word_simple', [])
    if len(word_simple) == 0:
        result += "No simple\n"
    else:
        result += 'Simple:\n'
        for simple in word_simple:
            simple_type = simple.get('simple_type', '')
            result += "%s\n" % simple_type
            word_details = simple.get('simple_details', '')
            for detail in word_details:
                result += colorful.red | "  - %s\n" % detail

    result += '\n'
    result += 'Descs:\n'
    word_descs = word_dict.get('word_descs', [])
    for desc in word_descs:
        word_type = desc.get('word_type', '')
        result += "%s\n" % word_type
        word_meanings = desc.get('meanings', '')
        for mean in word_meanings:
            cn_mean = mean.get('cn_mean', '')
            jp_mean = mean.get('jp_mean', '')
            sentences = mean.get('sentences', [])
            result += colorful.red | "  - %s    " % cn_mean
            result += "%s\n" % jp_mean
            for sentence in sentences:
                jp_sentence = sentence.get('sentence_jp', '')
                cn_sentence = sentence.get('sentence_cn', '')
                result += "    - %s    %s\n" % (jp_sentence, cn_sentence)
    return result