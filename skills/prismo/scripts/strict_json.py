"""Leitura JSON que recusa chaves duplicadas e números não finitos."""
import json


def _pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError('Chave JSON duplicada: ' + key)
        result[key] = value
    return result


def _constant(value):
    raise ValueError('Número JSON inválido: ' + value)


def loads(text):
    return json.loads(text, object_pairs_hook=_pairs, parse_constant=_constant)
