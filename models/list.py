import time

from utils.api_mal import get_anime_mal
from google.appengine.api.images import get_serving_url
from google.appengine.ext import ndb


class Watching(ndb.Model):
    id_utente = ndb.StringProperty(required=True)
    id_anime  = ndb.StringProperty(required=True)

    @classmethod
    def watch_key(cls, utente):
        return ndb.Key('Watching', utente)

    @classmethod
    def insert(cls, id_utente, id_anime):
        """
        Controlla nel datastore se e presente la coppia passata come
        parametro (id_utente, id_anime).
        In caso affermativo ritorna l'id della tupla, in caso non sia
        presente viene inserito.
        :param id_utente:
        :param id_anime:
        :return: None se non presente, la chiave della tupla se gia
        presente nel datastore.
        """
        Watching(
            parent=Watching.watch_key(id_utente),
            id_utente=id_utente,
            id_anime=id_anime
        ).put()

    @classmethod
    def get_watching_from_user(cls, id_utente):
        """
        Ritorna la lista dei watching in base al nome utente
        :param id_utente: username
        :return: lista watching
        """
        return Watching.query(
            ancestor=Watching.watch_key(id_utente)
        ).fetch()

    @classmethod
    def get_watching(cls, id_utente, id_anime):
        """
        Ritorna il watch di un particolare utente per un particolare anime
        :param id_utente:
        :param id_anime:
        :return:
        """
        watch = Watching.query(
            ancestor=Watching.watch_key(id_utente)
        ).filter(Watching.id_anime == id_anime).fetch()

        if watch:
            return watch[0]
        return None


class Like(ndb.Model):
    id_utente = ndb.StringProperty(required=True)
    id_anime  = ndb.StringProperty(required=True)

    @classmethod
    def like_key(cls, utente):
        return ndb.Key('Like', utente)

    @classmethod
    def insert(cls, id_utente, id_anime):
        """
        Controlla nel datastore se e presente la coppia passata come
        parametro (id_utente, id_anime).
        In caso affermativo ritorna l'id della tupla, in caso non sia
        presente viene inserito.
        :param id_utente:
        :param id_anime:
        :return: None se non presente, la chiave della tupla se gia
        presente nel datastore.
        """
        Like(
            parent=Like.like_key(id_utente),
            id_utente=id_utente,
            id_anime=id_anime
        ).put()

    @classmethod
    def get_like_from_user(cls, id_utente):
        """
        Ritorna la lista dei like in base al nome utente
        :param id_utente: username
        :return: lista like
        """
        return Like.query(
            ancestor=Like.like_key(id_utente)
        ).fetch()

    @classmethod
    def get_like(cls, id_utente, id_anime):
        """
        Ritorna il like di un particolare utente per un particolare anime
        :param id_utente:
        :param id_anime:
        :return:
        """
        like = Like.query(
            ancestor=Like.like_key(id_utente)
        ).filter(Like.id_anime == id_anime).fetch()

        if like:
            return like[0]
        return None
