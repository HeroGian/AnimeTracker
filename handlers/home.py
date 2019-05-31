import urllib
from utils.delete_ndb import delete
from utils.user import get_user_by_session
from models.anime import Anime
from models.recens import Recensione
from models.user import Utente
from jinja_setup import JENV
from handlers.base import BaseHandler
from google.appengine.api.images import get_serving_url


class MainHandler(BaseHandler):
    def get(self, template = JENV.get_template('index.html')):

        self.session['current_page'] = '/'

        user = get_user_by_session(self)

        # Prende le ultime n recensioni
        last_n_rec = Recensione.get_last_n_rece(n=5)

        last_n_anime = []
        for i in last_n_rec:
            anime = Anime.get_by_id(i.anime)
            if anime.blob_key:
                cover = get_serving_url(anime.blob_key)
            else:
                cover = anime.copertina
            last_n_anime.append(
                {
                    'cover': cover,
                    'key': str(anime.key.id()).decode('utf-8')
                }
            )
            i.recens = i.recens[:290] + '...'

        # Prende n anime in corso
        current_anime_tot = Anime.get_n_current_anime(n=10)

        current_anime = []
        for a in current_anime_tot:
            current_anime.append(
                {
                    'titolo': str(a.key.id()).replace(' ', '+').decode('utf-8'),
                    'cover': Anime.get_cover(a)
                }
            )
        # Prende la top 5 degli anime meglio votati
        top_5_anime_tot = Anime.get_top_n_anime(n=10)

        top_5_anime = []
        for a in top_5_anime_tot:
            top_5_anime.append(
                {
                    'titolo': str(a.key.id()).replace(' ', '+').decode('utf-8'),
                    'cover': Anime.get_cover(a)
                }
            )

        param = {
            'avatar': Utente.get_avatar(user),
            'user': user,
            'last_n_rec': last_n_rec,
            'last_n_anime': last_n_anime,
            'current_anime': current_anime,
            'top_5_anime': top_5_anime
        }

        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(template.render(param))

    def post(self):
        tipo_r = self.request.get('cosa_cerchi')
        query = self.request.get('search')
        query = unicode(query).encode('unicode_escape')

        self.redirect('/search?' + urllib.urlencode(
            {
                'type': tipo_r,
                'q': query
            }
        ))
