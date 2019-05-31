# coding: utf-8
import webapp2
from lxml import etree
from datetime import date
from handlers.base import BaseHandler
from models.anime import Anime
from models.recens import Recensione


class AnimeReceAPI(BaseHandler):
    def get(self):

        id_anime = self.request.get('id')

        if id_anime == '':
            webapp2.abort(code=400)

        anime = Anime.get_by_id(id_anime)

        if not anime:
            webapp2.abort(code=400)

        recensioni = Recensione.get_rece_from_anime(id_anime)

        root = etree.Element('reviews')

        for r in recensioni:
            entry = etree.Element('entry')

            autore = etree.SubElement(entry, 'author')
            autore.text = r.autore

            voto = etree.SubElement(entry, 'vote')
            voto.text = str(r.voto)

            data_ins = etree.SubElement(entry, 'date')
            data_ins.text = str(r.data_ins.date())

            comment = etree.SubElement(entry, 'comment')
            comment.text = r.recens

            root.append(entry)

        self.response.headers['Content-Type'] = 'application/xml'
        self.response.write(etree.tostring(root, pretty_print=True))
