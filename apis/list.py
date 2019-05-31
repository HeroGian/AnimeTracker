# coding: utf-8
import webapp2
from lxml import etree
from models.anime import Anime
from models.list import Watching
from models.user import Utente
from handlers.base import BaseHandler


class UserListAPI(BaseHandler):
    def get(self):

        id_utente = self.request.get('id')

        if id_utente == '':
            webapp2.abort(code=400, detail='inserire un username')

        user = Utente.get_by_id(id_utente)

        if not user:
            webapp2.abort(code=400, detail='username errato')

        name_list_watch = Watching.get_watching_from_user(user.key.id())
        list_watch = []
        for name in name_list_watch:
            list_watch.append(
                Anime.get_by_id(name.id_anime)
            )

        root = etree.Element('list')
        for a in list_watch:
            entry  = etree.Element('entry')

            titolo = etree.SubElement(entry, 'title')
            titolo.text = a.key.id().decode('utf-8')

            num_ep = etree.SubElement(entry, 'episodes')
            num_ep.text = str(a.num_ep)

            status = etree.SubElement(entry, 'status')
            status.text = a.status

            if a.start_date:
                start_date = etree.SubElement(entry, 'start_date')
                start_date.text = str(a.start_date)

            if a.end_date:
                end_date = etree.SubElement(entry, 'end_date')
                end_date.text = str(a.end_date)

            if a.voto_medio:
                voto = etree.SubElement(entry, 'score')
                voto.text = str(a.voto_medio)

            cover = etree.SubElement(entry, 'image')
            cover.text = Anime.get_cover(a)

            if a.descr:
                descr = etree.SubElement(entry, 'description')
                descr.text = a.descr

            root.append(entry)

        self.response.headers['Content-Type'] = 'application/xml'
        self.response.write(etree.tostring(root, pretty_print=True))

