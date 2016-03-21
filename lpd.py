#!/bin/env python3
# -*- coding: utf-8 -*-

import re

__version__ = '0.1.0'

debug_time = False


lpd = []

lpd_d = {}


def split_main_words(s):

    words = [word.strip().replace('|', '') for word in s.split(',')]

    news_words = [words[0]]
    for word in words[1:]:
        if word.endswith('\~'):
            new_word = words[0][len(word[:-2]):] + word[:-2]
            news_words.append(new_word)
        else:
            news_words.append(word)

    return news_words


def split_main_pss(s):
    """
    "ɪm, (¦ )em" => ['Im','em']
    """
    pss = [ps.strip() for ps in s.split(',')]
    pss = [re.sub('\(? *¦ *\)?', '', ps) for ps in pss]

    new_pss = []
    for ps in pss:
        if '-' in ps:
            # need some code here
            pass
        else:
            new_pss.append(ps)

    return pss


def ps_clean(ps):
    new_pss = re.sub('\[sup\].*\[/sup\]', '', ps
                     .replace('[i]', '(')
                     .replace('[/i]', ')')
                     .replace('[sub]([/sub]ˌ[sub])[/sub]', 'ˌ')
                     .replace('\xa0\xa0', ' ')
                     .replace('\xa0', '')
                     .replace('‿', '')
                     .replace('◂', ''))
    return new_pss


def split_lines(dsl_path):

    title_words_lines = []

    title_word = None
    lines = []

    for line in open(dsl_path, encoding='utf-16-le'):
        if line.startswith('#') or line.startswith(' '):
            continue

        elif line.startswith('\t'):
            lines.append(line)

        else:
            if lines:
                title_words_lines.append((title_word, lines))
                lines = []
            title_word = line.strip()

    title_words_lines.append((title_word, lines))

    return title_words_lines


def split_derivative_words(s):
    words = [one.strip() for one in s.split(',')]
    new_words = []
    if '\\~' in s:
        word = words[0]
        new_words.append(word)
        word_head = word.split('|')[0]

        for one in words[1:]:
            the_word = None
            if '\\~' in one:
                parts = [x for x in one.split('\\~') if x]
                if len(parts) == 1:
                    the_word = word_head + '|' + parts[0]
                elif len(parts) == 2:
                    the_word = parts[0] + word_head[len(parts[0]):] + '|' + parts[1]
                elif len(parts) == 3:
                    raise ValueError('what the hell: ', s)
            else:
                the_word = one

            new_words.append(the_word)

    return new_words or words


def analyse(title_word, lines):
    lis = []

    word_class = None
    main_pss = []

    for line in lines:

        # main main_words pattern ↓
        m = re.match('^\t\[m1\]'
                     '\[b\](?P<main_words>.+?)\[/b\]'
                     ' *'
                     # '(:?\[i\] *(?P<word_class>\S+)\[/i\])?'
                     '(:?\[i\](?P<word_class>.+?)\[/i\])?'
                     ' *'
                     '\[p\]BrE\[/p\]'
                     '.+?'
                     '\[c mediumblue\](?P<man_pss>.+?)\[/c\]', line)
        if m:

            main_words = tuple(split_main_words(m.group('main_words')))

            word_class = m.group('word_class').strip() if m.group('word_class') else None

            main_pss = split_main_pss(ps_clean(m.group('man_pss')))

            if ',' in main_pss and '|' in main_pss and debug_time:
                print(',| in main_pss:', main_pss)

            lis.append([main_words, word_class, main_pss])

            continue

        dm = re.match('^\t\[m1\]▷ '
                      '\[b\](?P<derivative_words>.+?)\[/b\]'
                      ' *'
                      '\[c mediumblue\](?P<sub_pss>.+?)\[/c\]', line)

        if dm:

            derivative_words = dm.group('derivative_words')

            if derivative_words.startswith('-'):
                derivative_words = title_word.split('|')[0] + '|' + derivative_words[1:]

            main_ps_head = main_pss[0].split('|')[0] if main_pss else ''

            sub_pss_str = ps_clean(dm.group('sub_pss'))

            # None
            if ',' in derivative_words and ',' in sub_pss_str:
                print('-----WTH-----', derivative_words, sub_pss_str)

            if ',' in dm.group('sub_pss') and debug_time:
                debug_print(', in sub_pss', title_word, main_pss, derivative_words, sub_pss_str)

            if '-' in dm.group('sub_pss') and debug_time:
                debug_print('- in sub_pss', title_word, main_pss, derivative_words, sub_pss_str)

            if '-' in dm.group('sub_pss') and '/' in dm.group('sub_pss') and debug_time:
                debug_print('(- and /) in sub_pss', title_word, main_pss, derivative_words, sub_pss_str)

            if '-' in dm.group('sub_pss') and ',' in dm.group('sub_pss') and debug_time:
                debug_print('(- and ,) in sub_pss', title_word, main_pss, derivative_words, sub_pss_str)

            derivative_words_list = []
            pss_list = []
            for derivative_word in split_derivative_words(derivative_words):

                # like:  noti|fier/s   faɪ‿ə/z
                m = re.match('^([a-zA-Z\']+)\|([a-zA-Z\']+)/([a-zA-Z\']+)$', derivative_word)
                if m:
                    sub_pss = sub_pss_str.split('/')
                    lis.append([m.group(1)+m.group(2), word_class, main_ps_head + sub_pss[0]])
                    try:
                        derivative_words_list.append(m.group(1)+m.group(2)+m.group(3))
                        pss_list.append(main_ps_head + sub_pss[0] + sub_pss[1])
                    except IndexError:
                        if debug_time:
                            debug_print('IndexError:', title_word, main_pss, derivative_word, sub_pss)
                    continue

                # like:  wrapping/s    ˈræp ɪŋ/z
                m = re.match('^([a-zA-Z\']+)/([a-zA-Z\']+)$', derivative_word)
                if m:
                    sub_pss = sub_pss_str.split('/')
                    lis.append([(m.group(1),), word_class, (sub_pss[0],)])
                    try:
                        derivative_words_list.append(m.group(1)+m.group(2))
                        pss_list.append(sub_pss[0] + sub_pss[1])
                    except IndexError:
                        if debug_time:
                            debug_print('IndexError:', title_word, main_pss, derivative_word, sub_pss)
                    continue

                # like:  pharisaic|al   əl
                m = re.match('^([a-zA-Z\']+)\|([a-zA-Z\']+)$', derivative_word)
                if m:
                    pss = []
                    for ps in sub_pss_str.split('/'):
                        pss.append(main_ps_head + ps)

                    derivative_words_list.append(m.group(1)+m.group(2))
                    pss_list.extend(pss)
                    continue

                # like:  zapped  zæpt
                m = re.match('^[a-zA-Z\']+$', derivative_word)
                if m:
                    derivative_words_list.append(derivative_word)
                    pss_list.extend(sub_pss_str.split('/'))
                    continue
            lis.append([derivative_words_list, word_class, pss_list])

    return lis


def debug_print(info=None, title_words=None, main_pss=None, derivative_words=None, sub_pss=None):
    print(info)
    print('    title_words:      {:20}, man_pss: {}'.format(title_words, main_pss))
    print('    derivative_words: {:20}, sub_pss: {}'.format(derivative_words, sub_pss))
    print()


def load(dsl_path):
    global lpd

    title_words_lines = split_lines(dsl_path)
    for title_word, lines in title_words_lines:
        lpd.extend(analyse(title_word, lines))

    qut = 0
    for one in lpd:
        qut += len(one[0])
    if debug_time:
        print('Quantity of items:', len(lpd))
        print('Quantity of words:', qut)
    make_lpd_d()


def make_lpd_d():
    for item in lpd:
        for word in item[0]:

            if word not in lpd_d.keys():
                lpd_d[word] = {}

            if item[1] not in lpd_d[word].keys():
                lpd_d[word][item[1]] = []

            for ps in item[2]:
                if ps not in lpd_d[word][item[1]]:
                    lpd_d[word][item[1]].append(ps)


def find_old(word):
    items = []
    for item in lpd:
        if word.lower() in [word.lower() for word in item[0]]:
            items.append(item)
    return items


def find(word):
    return lpd_d[word]


def main():
    import sys
    import os
    load(dsl_path=os.path.expanduser('~')+os.sep+'En-En-Longman_Pronunciation.dsl')

    print(find(sys.argv[1]))

    for one in lpd:
        pass


if __name__ == '__main__':
    debug_time = True
    main()
