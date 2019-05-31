#!/usr/bin/env python
# -*- coding: utf-8 -*-
from random import shuffle
from utils.api_mal import get_anime_mal
from google.appengine.api.images import get_serving_url
from google.appengine.ext import ndb


class Anime(ndb.Model):
    search_id = ndb.ComputedProperty(lambda self: self.key.id().lower())
    blob_key  = ndb.BlobKeyProperty()
    copertina = ndb.StringProperty()
    num_ep = ndb.IntegerProperty()
    descr  = ndb.TextProperty()
    status = ndb.StringProperty(required=True)
    start_date = ndb.DateProperty()
    end_date   = ndb.DateProperty()
    voto_medio = ndb.FloatProperty()

    @classmethod
    def insert(cls, titolo, num_ep, descr,
               status, start_date, end_date, **kwargs):
        """
        Permette l'inserimento di un anime nel datastore.
        L'anime puo essere inserito manualmente oppure tramite le
        API di MyAnimeList.
        :param titolo: Titolo dell'anime
        :param num_ep: Numero di episodi di cui si compone
        :param descr: Breve descrizione
        :param status: Stato, se terminato, in onda, ecc
        :param start_date: Data di inizio
        :param end_date: Data di fine
        :param kwargs: Permette di passare copertina o blob_key
        :return: chiave dell'anime appena inserito
        """

        a = cls.get_by_id(titolo)

        if not a:
            a = Anime(id=titolo)

        a.descr  = descr
        a.num_ep = num_ep
        a.status = status

        if start_date:
            a.start_date = start_date

        if end_date:
            a.end_date = end_date

        blob_key = kwargs.get('blob_key')

        if blob_key:
            a.blob_key = blob_key
        else:
            a.copertina = kwargs.get('copertina')

        key = a.put()

        return key

    @classmethod
    def get_anime_from_title(cls, title, mal_info):
        """
        Ritorna la lista di anime il cui titolo contiene la stringa
        passata come argomento.
        Nel caso in cui la query sul db sia vuota, viene effettuata
        una richiesta sulle API di MyAnimeList.
        :param title: stringa
        :return: lista di anime
        """
        anime = Anime.query().filter(
            Anime.search_id >= title.lower()
        ).fetch()

        anime_match = []
        for a in anime:
            if title.lower() in a.key.id().lower().decode('utf-8'):
                if a.blob_key:
                    copertina = get_serving_url(a.blob_key)
                else:
                    copertina = a.copertina
                anime_match.append(
                    {'titolo': a.key.id().decode('utf-8'),
                     'copertina': copertina,
                     'num_ep': a.num_ep,
                     'descr': a.descr,
                     'status': a.status,
                     'start_date': a.start_date,
                     'end_date': a.end_date
                     }
                )

        # Se nel DB non sono presenti anime vado a richiamare
        # le API di MyAnimeList
        if not anime_match and (mal_info['tipo'] == 'mal_user'):
            # Preparo la lista da ritornare
            anime_match = get_anime_mal(
                title,
                username=mal_info['username'],
                password=mal_info['password']
            )
            # Inserisco quanto ottenuto dalle API nel DB interno
            for a in anime_match:
                Anime.insert(
                    titolo=a['titolo'],
                    num_ep=a['num_ep'],
                    descr=a['descr'],
                    status=a['status'],
                    start_date=a['start_date'],
                    end_date=a['end_date'],
                    copertina=a['copertina']
                )

        return anime_match

    @classmethod
    def get_score_from_title(cls, title):
        """
        Dato un anime ritorna la media del suo punteggio
        :param title:
        :return: media punteggio anime come float
        """
        punteggio = Anime.get_by_id(title).voto_medio

        if not punteggio:
            return 'N/A'
        else:
            return punteggio

    @classmethod
    def get_n_current_anime(cls, n):
        """
        Ritorna gli anime attualmente in corso
        :param n: permette di specificare quanti anime si vuole
        :return: lista di anime
        """
        anime_list = Anime.query(
            Anime.status == 'Currently Airing'
        ).fetch()

        shuffle(anime_list)

        return anime_list[:n]

    @classmethod
    def get_top_n_anime(cls, n):
        """
        Ritorna la lista degli anime meglio votati
        :param n:
        :return:
        """
        return Anime.query().order(
            -Anime.voto_medio
        ).fetch(n)

    @classmethod
    def get_cover(cls, anime):
        if anime.blob_key:
            return get_serving_url(anime.blob_key)
        return anime.copertina
