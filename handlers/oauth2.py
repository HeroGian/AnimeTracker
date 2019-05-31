# coding: utf-8

import httplib2
import webapp2
import urllib
from jinja_setup import JENV
from httplib import HTTPException
from datetime import datetime
from utils.user import get_user_by_session
from models.anime import Anime
from models.user import Utente
from apiclient.discovery import build
from google.appengine.api import memcache
from handlers.base import BaseHandler
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import OAuth2Credentials
from validate_email import validate_email


google_plus_scopes  = 'https://www.googleapis.com/auth/plus.login ' \
                      'https://www.googleapis.com/auth/plus.me ' \
                      'https://www.googleapis.com/auth/userinfo.email'

google_calen_scopes = 'https://www.googleapis.com/auth/calendar'


class Oauth2Handler(BaseHandler):
    def get(self):

        current_page = self.session['current_page']

        if 'plus' in current_page:
            scope = google_plus_scopes
        else:
            scope = google_calen_scopes

        flow = flow_from_clientsecrets(
            'client_secret.json',
            scope=scope,
            redirect_uri='https://animetracker-sar.appspot.com/oauth2callback'
        )

        # Step1 del protocollo oauth2
        if not self.request.get('code'):
            try:
                auth_uri = flow.step1_get_authorize_url()
                print 'Step1 completato'
                return self.redirect(str(auth_uri))
            except HTTPException:
                return webapp2.abort(code=503)

        # L'utente ha premuto rifiuta sulla pagina di autorizzazione
        # viene ridirezionato sulla pagina chiamante
        elif self.request.get('error'):
            self.redirect(current_page)

        # Step2 del protocollo oauth2
        else:
            auth_code = self.request.get('code')
            try:
                credentials = flow.step2_exchange(auth_code)
                print 'Step2 completato'
            except HTTPException:
                return webapp2.abort(code=503)

            # Salvataggio credenziali e redirezione
            if 'calendar' in current_page:
                print 'salvo credenziali calendar'
                self.session['gcal_cred'] = credentials.to_json()

            else:
                print 'salvo credenziali google plus'
                self.session['gplus_cred'] = credentials.to_json()

            self.redirect(current_page.encode('utf-8'))


class CalendarHandler(BaseHandler):
    def get(self):

        lista_url = self.request.get('list')
        user  = get_user_by_session(self)
        user  = Utente.get_by_id(user)

        items = lista_url.split('+')

        lista = []
        for i in items:
            lista.append(i.replace('_', ' '))

        self.session['current_page'] = '/calendar?' + urllib.urlencode(
            {
                'list': lista_url.encode('utf-8')
            }
        )

        if 'gcal_cred' not in self.session:
            print 'Credenziali non trovate'
            return self.redirect('/oauth2callback')

        json_creden = self.session['gcal_cred']
        credentials = OAuth2Credentials.from_json(s=json_creden)

        if credentials.access_token_expired:
            print 'Credenziali non valide'
            return self.redirect('/oauth2callback')

        http = httplib2.Http(cache=memcache)
        http_auth = credentials.authorize(http=http)

        try:
            calendar_service = build('calendar', 'v3', http=http_auth)
        except HTTPException:
            return webapp2.abort(code=503)

        print lista[0].encode('utf-8')

        count = 0

        if lista:
            oggi  = datetime.now().date()

            for item in lista:

                a = Anime.get_by_id(item)

                if a.start_date and a.start_date > oggi:
                    event = {
                        'summary': a.key.id(),
                        'description': 'Data di inizio di {}'.format(a.key.id()),
                        'start': {
                            'date': str(a.start_date),
                            'timeZone': 'Europe/Rome',
                        },
                        'end': {
                            'date': str(a.start_date),
                            'timeZone': 'Europe/Rome',
                        }
                    }
                    calendar_service.events().insert(
                        calendarId='primary',
                        body=event
                    ).execute()

                    count += 1

                    print str(a.key.id()) + ' inserito nel calendario'

        self.session['added_calendar'] = count
        self.redirect('/profile?id=' + user.key.id())


class SignUpPlusHandler(BaseHandler):
    def get(self):

        self.session['current_page'] = '/signup_plus'

        if 'gplus_cred' not in self.session:
            return self.redirect('/oauth2callback')

        json_creden = self.session['gplus_cred']
        credentials = OAuth2Credentials.from_json(s=json_creden)

        if credentials.access_token_expired:
            return self.redirect('/oauth2callback')

        http = httplib2.Http(cache=memcache)
        http_auth = credentials.authorize(http=http)

        try:
            gplus_service = build('plus', 'v1', http=http_auth)
        except HTTPException:
            return webapp2.abort(code=503)
        gplus_resp = gplus_service.people().get(userId='me').execute(http=http_auth)

        params = {
            'id_account': gplus_resp['id'],
            'nome': gplus_resp['name']['givenName'],
            'cognome': gplus_resp['name']['familyName'],
            'username': gplus_resp['displayName'],
            'email': gplus_resp['emails'][0]['value'],
            'image': gplus_resp['image']['url'].replace('sz=50', 'sz=150')
        }
        t = JENV.get_template('signup_plus.html')

        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(t.render(params))

    def post(self):
        avatar_url = self.request.get('image_url')
        id_account = self.request.get('id_account')
        username = self.request.get('username')
        cognome  = self.request.get('lastname')
        nome  = self.request.get('firstname')
        email = self.request.get('email')

        params = {
            'id_account': id_account,
            'nome': nome,
            'cognome': cognome,
            'username': username,
            'email': email,
            'image': avatar_url,
        }

        valid = validate_email(email)

        if nome == '':
            params['nome_err'] = 'inserisci il tuo nome'

        if cognome == '':
            params['cognome_err'] = 'inserisci il tuo cognome'

        if email == '':
            params['email_err'] = 'inserisci un indirizzo email'
        elif not valid:
            params['email_err'] = 'l\'indirizzo email inserito non e valido'

        if username == '':
            params['username_err'] = 'inserisci un username'

        # Controllo se qualche flag di errore e settato
        err_check = False
        for k in params.keys():
            if 'err' in k:
                err_check = True
                break

        # L'utente non ha immesso errori
        if not err_check:
            ret = Utente.get_or_insert(
                username = username,
                associated_user=id_account,
                email = email,
                nome = nome,
                cognome = cognome,
                tipo = 'google_user',
                avatar_url = avatar_url,
            )

            if ret == 0:
                return self.redirect('/')

            elif ret == 1:
                params['username_err'] = 'l\' username inserito esiste gia'
                params['username'] = ''

            elif ret == 2:
                params['username_err'] = 'il tuo id Google+ e gia associato ad un account'
                params['username'] = ''

            elif ret == 3:
                params['email_err'] = 'l\'indirizzo email non e disponibile'
                params['email'] = ''

            t = JENV.get_template('signup_plus.html')
            self.response.headers['Content-Type'] = 'text/html'
            self.response.write(t.render(params))

        # L'utente ha immesso errori
        else:
            t = JENV.get_template('signup_plus.html')
            self.response.headers['Content-Type'] = 'text/html'
            self.response.write(t.render(params))


class LoginPlusHandler(BaseHandler):
    def get(self):

        self.session['current_page'] = '/login_plus'

        if 'gplus_cred' not in self.session:
            return self.redirect('/oauth2callback')

        json_creden = self.session['gplus_cred']
        credentials = OAuth2Credentials.from_json(s=json_creden)

        if credentials.access_token_expired:
            return self.redirect('/oauth2callback')

        http = httplib2.Http(cache=memcache)
        http_auth = credentials.authorize(http=http)

        try:
            gplus_service = build('plus', 'v1', http=http_auth)
            print 'Build service completato'
        except HTTPException:
            return webapp2.abort(code=503)
        gplus_resp = gplus_service.people().get(userId='me').execute(http=http_auth)
        print 'Richiesta completata'

        user = Utente.get_from_associated(gplus_resp['id'])
        if user:

            self.session['type'] = 'google_user'
            self.session['user_name'] = user.key.id()
            self.session['name'] = user.nome
            self.session['last_name'] = user.cognome

            self.redirect('/')
        else:
            self.redirect('/login')
