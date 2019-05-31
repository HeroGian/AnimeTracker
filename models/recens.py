from models.anime import Anime
from google.appengine.ext import ndb


class Recensione(ndb.Model):
    anime  = ndb.StringProperty(required=True)
    autore = ndb.StringProperty(required=True)
    recens = ndb.TextProperty(required=True)
    voto = ndb.IntegerProperty(required=True)
    data_ins = ndb.DateTimeProperty(auto_now_add=True)

    @classmethod
    def recens_key(cls, titolo):
        return ndb.Key('Recensione', titolo)

    @classmethod
    def insert(cls, anime, autore, recens, voto):
        """
        Permette l'inserimento di una nuova recensione
        :param anime: anime recensito
        :param autore: autore che rilascia la recensione
        :param recens: commento della recensione
        :param voto: voto attribuito all'anime
        :return: La chiave della recensione inserita
        """
        new_r = Recensione(
            parent=Recensione.recens_key(anime),
            anime=anime,
            autore=autore,
            recens=recens,
            voto=voto
        )
        key = new_r.put()

        # Aggiorno la media dei voti dell'anime
        recens = Recensione.query(
            ancestor=Recensione.recens_key(anime)
        ).fetch()

        media_voti = 0
        for v in recens:
            media_voti += v.voto
        media_voti = round(float(media_voti) / len(recens), 1)

        anime = Anime.get_by_id(anime)
        anime.voto_medio = media_voti
        anime.put()

        return key

    @classmethod
    def get_last_n_rece(cls, n):
        """
        Ritorna le ultime n-recensioni ordinate per data
        :param n: numero di recensioni che si intende ottenere
        :return: lista di recensioni
        """
        return Recensione.query().order(-Recensione.data_ins).fetch(n)

    @classmethod
    def get_rece_from_anime(cls, title):
        """
        Ritorna le recensioni di un anime
        :param title: titolo dell'anime
        :return:
        """
        return Recensione.query(
            ancestor=Recensione.recens_key(title)
        ).fetch()

