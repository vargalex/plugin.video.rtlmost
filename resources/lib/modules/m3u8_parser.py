# coding: utf-8
# Copyright 2014 Globo.com Player authors. All rights reserved.
# Use of this source code is governed by a MIT License
# license that can be found in the LICENSE file.

import datetime
import itertools
import re


ATTRIBUTELISTPATTERN = re.compile(r'''((?:[^,"']|"[^"]*"|'[^']*')+)''')


def parse(content):
    data = []

    state = {'expect_playlist': False}

    lineno = 0
    for line in string_to_lines(content):
        lineno += 1
        line = line.strip()

        if line.startswith('#EXT-X-STREAM-INF'):
            state['expect_playlist'] = True
            _parse_stream_inf(line, data, state)

        # Comments and whitespace
        elif line.startswith('#'):
            # comment
            pass

        elif line.strip() == '':
            # blank lines are legal
            pass

        elif state['expect_playlist']:
            _parse_variant_playlist(line, data, state)
            state['expect_playlist'] = False

    return data


def _parse_attribute_list(prefix, line, atribute_parser):
    params = ATTRIBUTELISTPATTERN.split(line.replace(prefix + ':', ''))[1::2]

    attributes = {}
    for param in params:
        name, value = param.split('=', 1)
        name = normalize_attribute(name)

        if name in atribute_parser:
            value = atribute_parser[name](value)

            attributes[name] = value

    return attributes


def _parse_stream_inf(line, data, state):
    atribute_parser = remove_quotes_parser('resolution')
    #atribute_parser["bandwidth"] = lambda x: int(float(x))
    state['stream_info'] = _parse_attribute_list('#EXT-X-STREAM-INF', line, atribute_parser)


def _parse_variant_playlist(line, data, state):
    try:
        playlist = {'uri': line,
                'resolution': state['stream_info']['resolution']}

        data.append(playlist)
    except:
        pass


def string_to_lines(string):
    return string.strip().replace('\r\n', '\n').split('\n')


def remove_quotes_parser(*attrs):
    return dict(zip(attrs, itertools.repeat(remove_quotes)))


def remove_quotes(string):
    '''
    Remove quotes from string.

    Ex.:
      "foo" -> foo
      'foo' -> foo
      'foo  -> 'foo

    '''
    quotes = ('"', "'")
    if string and string[0] in quotes and string[-1] in quotes:
        return string[1:-1]
    return string


def normalize_attribute(attribute):
    return attribute.replace('-', '_').lower().strip()
