from random import choice
import requests

api_url = 'https://stepik.akentev.com/api/millionaire'


def q_and_a(level):
    m = {}
    if level == 1:
        r = requests.get(api_url, params={'complexity': '1'}).json()
    elif level == 2:
        r = requests.get(api_url, params={'complexity': '2'}).json()
    else:
        r = requests.get(api_url, params={'complexity': '3'}).json()
    q = r['question']
    a = r['answers']
    m[q] = {True: a[0]}
    a.pop(0)
    m[q][False] = a
    return m
