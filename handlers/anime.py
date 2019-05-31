import urllib
import webapp2
from datetime import datetime
from utils.user import get_user_by_session
from models.anime import Anime
from models.recens import Recensione
from models.user import Utente
from models.list import Like, Watching
from jinja_setup import JENV
from handlers.base import BaseHandler
from google.appengine.api.images import get_serving_url


def get_params(obj, id_anime):
    """
    Dato l'idenfificativo di un anime ritorna i parametri da
    renderizzare sulla pagina di un anime
    :param obj: riferimento all'handler
    :param id_anime: identificativo di un anime
    :return: ritorna un dizionario contenente username, avatar, punteggio
    anime, titolo anime, copertina anime, e recensioni
    """

    # Preleva informazioni dell'utente dalla sessione
    user = get_user_by_session(obj)

    # Anime corrente
    ani = Anime.get_by_id(id_anime)

    if not ani:
        webapp2.abort(code=404)

    ani = ani.key.get()

    # Recensioni dell'anime
    rece = Recensione.get_rece_from_anime(id_anime)

    # Avatar degli utenti che hanno recensito
    avatar_recens = []
    for r in rece:
        avatar_recens.append(
            Utente.get_avatar(r.autore)
        )

    # prelevo la copertina dell'anime
    if ani.blob_key:
        copertina = get_serving_url(ani.blob_key)
    else:
        copertina = ani.copertina

    # determino se l'anime e stato aggiunto alle liste dell'utente
    seguito  = None
    mi_piace = None
    if user:
        mi_piace = Like.get_like(user, id_anime)
        seguito  = Watching.get_watching(user, id_anime)

    # Parametri da passare al template anime
    params = {
        'user': user,
        'avatar': Utente.get_avatar(user),
        'punteggio': Anime.get_score_from_title(ani.key.id()),
        'titolo': ani.key.id().decode('utf-8'),
        'copertina': copertina,
        'ani': ani,
        'rece': rece,
        'avatar_recens': avatar_recens,
        'mi_piace': mi_piace,
        'seguito': seguito,
        'share_url': str(obj.request.url).replace('+', '_')
    }

    return params


class AnimeInfoHandler(BaseHandler):
    def get(self, template = JENV.get_template('anime.html')):

        id_anime = self.request.get('id')
        id_anime = id_anime.replace('_', ' ')

        if not id_anime:
            webapp2.abort(code=404)

        self.session['current_page'] = '/anime?' + urllib.urlencode(
                {
                    'id': id_anime.encode('utf-8')
                }
        )

        params = get_params(self, id_anime)

        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(template.render(params))

    def post(self):

        id_anime = self.request.get('id')
        id_anime = id_anime.replace('_', ' ')

        if not id_anime:
            webapp2.abort(code=404)

        params = get_params(self, id_anime)

        # Se e stato premuto il bottone per inserire una recensione
        if self.request.get('submit_rece'):
            voto = self.request.get('voto')
            rece = self.request.get('rece')
            id_anime = self.request.get('id')

            Recensione.insert(
                anime=id_anime,
                autore=self.session['user_name'],
                recens=rece,
                voto=int(voto)
            )
            self.redirect('/anime?' + urllib.urlencode(
                {'id': id_anime.encode('utf-8')}
            ))

        # Se e stato premuto il bottone mi piace
        elif self.request.get('anime_fav'):
            id_anime = self.request.get('id')
            Like.insert(
                id_utente=self.session['user_name'],
                id_anime=id_anime
            )
            self.redirect('/anime?' + urllib.urlencode(
                {'id': id_anime.encode('utf-8')}
            ))

        # Se e stato premuto il bottone aggiungi alla lista
        elif self.request.get('anime_add'):
            id_anime = self.request.get('id')
            Watching.insert(
                id_utente=self.session['user_name'],
                id_anime=id_anime
            )
            self.redirect('/anime?' + urllib.urlencode(
                {'id': id_anime.encode('utf-8')}
            ))

        # Se e stato premuto il bottone per modificare la descrizione
        elif self.request.get('edit_descr'):

            params['edit_descr'] = True

            t = JENV.get_template('anime.html')
            self.response.headers['Content-Type'] = 'text/html'
            self.response.write(t.render(params))

        # Se e stato premuto il bottone per modificare le info
        elif self.request.get('edit_info'):

            params['edit_info'] = True

            t = JENV.get_template('anime.html')
            self.response.headers['Content-Type'] = 'text/html'
            self.response.write(t.render(params))

        # Premuto bottone conferma modifica descrizione
        elif self.request.get('confirm_edit_descr'):
            descr = self.request.get('descr')
            id_anime = self.request.get('id')

            # evita code injection
            descr = descr.replace('<', '&lt;')
            descr = descr.replace('>', '&gt;')

            a = Anime.get_by_id(id_anime)
            a.descr = descr.encode('utf-8')
            a.put()

            self.redirect('/anime?' + urllib.urlencode(
                {'id': id_anime.encode('utf-8')}
            ))

        # Premuto bottone conferma modifica informazioni
        elif self.request.get('confirm_edit_info'):
            episodi = self.request.get('episodi')
            start_date = self.request.get('start_date')
            end_date = self.request.get('end_date')
            status = self.request.get('status')
            id_anime = self.request.get('id')

            if episodi == '':
                episodi = 0

            if start_date != '':
                start_date = datetime.strptime(
                    str(start_date),
                    '%Y-%m-%d'
                ).date()
            else:
                start_date = None

            if end_date != '':
                end_date = datetime.strptime(
                    str(end_date),
                    '%Y-%m-%d'
                ).date()
            else:
                end_date = None

            a = Anime.get_by_id(id_anime)
            a.num_ep = int(episodi)
            a.start_date = start_date
            a.end_date = end_date
            a.status = status
            a.put()

            self.redirect('/anime?' + urllib.urlencode(
                {'id': id_anime.encode('utf-8')}
            ))

        # Bottone esci per le modifiche
        elif self.request.get('close_edit_descr'):
            self.redirect('/anime?' + urllib.urlencode(
                {'id': id_anime.encode('utf-8')}
            ))

        elif self.request.get('del_anime_fav'):
            Like.get_like(params['user'], id_anime).key.delete()
            self.redirect('/anime?' + urllib.urlencode(
                {'id': id_anime.encode('utf-8')}
            ))

        elif self.request.get('del_anime_add'):
            Watching.get_watching(params['user'], id_anime).key.delete()
            self.redirect('/anime?' + urllib.urlencode(
                {'id': id_anime.encode('utf-8')}
            ))
