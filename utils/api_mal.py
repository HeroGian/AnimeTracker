import urllib
import httplib2
from httplib import HTTPException
from xml.etree import ElementTree
from datetime import datetime
from google.appengine.api import memcache


def check_mal_account(username, passw):
    """
    Permette di verificare se l'username esiste su MyanimeList
    :param username: nome utente
    :param passw: password
    :return: True se esiste, False se non esiste
    """
    base_url = 'https://myanimelist.net/api/account/verify_credentials.xml'

    h = httplib2.Http(cache=memcache)
    h.add_credentials(username, passw)

    r, content = h.request(
        base_url,
        'GET'
    )

    if content != 'Invalid credentials':
        return True
    return False


def get_anime_mal(titolo, username, password):
    """
    Dato il titolo di un anime ritorna la lista degli anime presenti
    su MyAnimeList che matchano la query di ricerca
    :param titolo: titolo anime
    :param username: username utente che effettua la ricerca
    :param password: password utente0
    :return: lista di anime
    """

    base_url  = 'http://myanimelist.net/api/anime/search.xml?'
    query = urllib.urlencode({'q': titolo})

    h = httplib2.Http(cache=memcache)
    h.add_credentials(username, password)

    r, content = h.request(
        base_url + query,
        'GET'
    )

    anime_match = []

    if not content or content == '':
        return anime_match

    tree = ElementTree.fromstring(content)

    for e in tree:

        titolo = e.find('title').text
        status = e.find('status').text
        num_ep = int(e.find('episodes').text)
        descr  = e.find('synopsis').text

        copertina  = e.find('image').text
        start_date = str(e.find('start_date').text)
        end_date   = str(e.find('end_date').text)

        if '00' not in start_date:
            start_date = datetime.strptime(
                start_date,
                '%Y-%m-%d'
            ).date()
        else:
            start_date = None

        if '00' not in end_date:
            end_date = datetime.strptime(
                end_date,
                '%Y-%m-%d'
            ).date()
        else:
            end_date = None

        a = {
            'copertina': copertina,
            'titolo': titolo,
            'num_ep': num_ep,
            'descr' : descr,
            'status': status,
            'start_date': start_date,
            'end_date': end_date
        }

        anime_match.append(a)

    return anime_match
