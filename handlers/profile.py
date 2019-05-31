# coding: utf-8
import urllib
import webapp2
from utils.user import get_user_by_session
from models.user import Utente
from models.list import Like, Watching
from models.anime import Anime
from jinja_setup import JENV
from handlers.base import BaseHandler
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers


def get_params(obj):

    # preleva l'utente dalla sessione
    user = get_user_by_session(obj)

    # pagina utente che stiamo guardando
    username_page = obj.request.get('id')

    obj.session['current_page'] = '/profile?id=' + str(username_page)

    # nessun parametro passato da url
    if not username_page:
        webapp2.abort(code=404)

    # utente corrente
    user_page = Utente.get_by_id(username_page)

    # il parametro non esiste
    if not user_page:
        webapp2.abort(code=404)

    # liste dell'utente della pagina
    lista_like  = Like.get_like_from_user(username_page)
    lista_watch = Watching.get_watching_from_user(username_page)

    # riempie le liste con gli anime seguiti e preferiti

    lista_like_com = []
    for a in lista_like:
        lista_like_com.append(
            {
                'titolo': a.id_anime,
                'cover': Anime.get_cover(Anime.get_by_id(a.id_anime))
            }
        )
    lista_watch_com = []
    for a in lista_watch:
        lista_watch_com.append(
            {
                'titolo': a.id_anime,
                'cover': Anime.get_cover(Anime.get_by_id(a.id_anime))
            }
        )

    aggiunti_calendario = None
    if 'added_calendar' in obj.session:
        num = obj.session['added_calendar']
        del obj.session['added_calendar']
        if num == 0:
            aggiunti_calendario = 'non ho aggiunto anime al tuo calendario :-('
        else:
            aggiunti_calendario = 'ho aggiunto {} anime al tuo calendario :-)'.format(num)

    params = {
        'avatar_header': Utente.get_avatar(user),
        'avatar_page': Utente.get_avatar(username_page),
        'user_page': user_page,
        'user': user,
        'lista_like': lista_like_com,
        'lista_watch': lista_watch_com,
        'upload_url': blobstore.create_upload_url('/profile'),
        'aggiunti_calendario': aggiunti_calendario
    }

    return params


class ProfileHandler(BaseHandler, blobstore_handlers.BlobstoreUploadHandler):
    def get(self, template = JENV.get_template('profile.html')):

        params = get_params(self)

        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(template.render(params))

    def post(self):

        user = get_user_by_session(self)

        # Se premuto il bottone per inserire un avatar
        if self.request.get('submit'):
            blob_key = self.get_uploads()
            if blob_key:
                blob_key = blob_key[0].key()
                Utente.insert_avatar(username=user, blob_key=blob_key)

            self.redirect('/profile?' + urllib.urlencode(
                {'id': user}
            ))

        # Se premuto il bottone per cancellare l'avatar
        elif self.request.get('delete'):
            Utente.delete_avatar(user)
            self.redirect('/profile?' + urllib.urlencode(
                {'id': user}
            ))

        # Se premuto il bottone per cancellare i like
        elif self.request.get('del_like'):
            delete_list = self.request.get_all('check_del_like')
            for a in delete_list:
                Like.get_like(user, a.encode('utf-8')).key.delete()
            self.redirect('/profile?' + urllib.urlencode(
                {'id': user}
            ))

        # Se premuto il bottone per cancellare i watch
        elif self.request.get('del_watch'):
            delete_list = self.request.get_all('check_del_watch')
            for a in delete_list:
                Watching.get_watching(user, a.encode('utf-8')).key.delete()
            self.redirect('/profile?' + urllib.urlencode(
                {'id': user}
            ))

        # Se premuto il bottone per il calendario
        elif self.request.get('add_calendar'):
            query_list = Watching.get_watching_from_user(user)

            calendar_list = []
            for c in query_list:
                calendar_list.append(c.id_anime)

            if query_list:
                param = '+'.join(calendar_list).replace(' ', '_')
            else:
                param = ""

            url = urllib.urlencode(
                {
                    'list': param.encode('utf-8')
                }
            )
            self.redirect('/calendar?' + url)

        elif self.request.get('edit_profile'):

            params = get_params(self)

            params['edit_profile'] = True

            t = JENV.get_template('profile.html')

            self.response.headers['Content-Type'] = 'text/html'
            self.response.write(t.render(params))

        elif self.request.get('close_edit_profile'):
            self.redirect('/profile?' + urllib.urlencode(
                {'id': user}
            ))
