import webapp2
import urllib
from utils.user import get_user_by_session
from models.anime import Anime
from models.user import Utente
from jinja_setup import JENV
from handlers.base import BaseHandler
from httplib import HTTPException


class SearchHandler(BaseHandler):
    def get(self, template = JENV.get_template('search.html')):

        query = self.request.get('q')
        tipo  = self.request.get('type')

        self.session['current_page'] = '/search?' + urllib.urlencode(
            {'type': tipo, 'q': query}
        )

        user = get_user_by_session(self)

        # Richiesta una ricerca di anime
        if tipo == 'anime':
            mal_info = {
                'tipo': None,
                'username': None,
                'password': None
            }

            if user:
                tipo = self.session['type']
                mal_info['tipo'] = tipo
                if tipo == 'mal_user':
                    mal_info['username'] = self.session['mal_name']
                    mal_info['password'] = self.session['mal_pass']

            try:
                lista_anime = Anime.get_anime_from_title(
                    title=query,
                    mal_info=mal_info
                )

                params = {
                    'user': user,
                    'avatar': Utente.get_avatar(user),
                    'lista_anime': lista_anime,
                    'query': query,
                    'type': 1
                }
                self.response.headers['Content-Type'] = 'text/html'
                self.response.write(template.render(params))

            except HTTPException:
                webapp2.abort(code=503)

        elif tipo == 'utenti':
            lista_utenti = Utente.get_user_from_name(query)

            params = {
                'user': user,
                'avatar': Utente.get_avatar(user),
                'lista_utenti': lista_utenti,
                'query': query,
                'type': 2
            }
            self.response.headers['Content-Type'] = 'text/html'
            self.response.write(template.render(params))
