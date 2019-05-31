import webapp2
from httplib import HTTPException
from utils.api_mal import check_mal_account
from jinja_setup import JENV
from handlers.base import BaseHandler
from models.user import Utente
from validate_email import validate_email


class SignUpHandler(BaseHandler):
    def get(self, template = JENV.get_template('signup.html')):
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(template.render())

    def post(self):
        user_name = self.request.get('username')
        firstname = self.request.get('firstname')
        last_name = self.request.get('lastname')
        email = self.request.get('email')
        password = self.request.get('password')

        valid = validate_email(email)

        errors = {}

        if user_name == '':
            errors['username_err'] = 'inserisci un username'
        else:
            errors['username'] = user_name

        if firstname == '':
            errors['firstname_err'] = 'inserisci il tuo nome'
        else:
            errors['firstname'] = firstname

        if last_name == '':
            errors['last_name_err'] = 'inserisci il tuo cognome'
        else:
            errors['last_name'] = last_name

        if email == '':
            errors['email_err'] = 'inserisci un indirizzo email'
        elif not valid:
            errors['email_err'] = 'l\'indirizzo email inserito non e valido'
        else:
            errors['email'] = email

        if len(password) <= 3:
            errors['password_err'] = 'la password deve contenere almeno 3 caratteri'

        err_check = False
        for k in errors.keys():
            if 'err' in k:
                err_check = True
                break

        if not err_check:
            ret = Utente.get_or_insert(
                username=user_name,
                email=email,
                passw=password,
                nome=firstname,
                cognome=last_name,
                tipo='normal_user'
            )

            if ret == 0:
                current_page = self.session['current_page']
                return self.redirect(current_page)

            elif ret == 1:
                errors['username_err'] = 'l\' username inserito esiste gia'
                errors['username'] = ''

            elif ret == 3:
                errors['email_err'] = 'l\' email non e disponibile'
                errors['email'] = ''

            t = JENV.get_template('signup.html')
            self.response.headers['Content-Type'] = 'text/html'
            self.response.write(t.render(errors))

        else:
            t = JENV.get_template('signup.html')
            self.response.headers['Content-Type'] = 'text/html'
            self.response.write(t.render(errors))


class SignUpMalHandler(BaseHandler):
    def get(self, template = JENV.get_template('signup_mal.html')):
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(template.render())

    def post(self, template = JENV.get_template('signup_mal.html')):
        if self.request.get('verifica'):
            username = self.request.get('username')
            password = self.request.get('password')

            try:
                verified = check_mal_account(
                    username=username,
                    passw=password
                )

                params = {
                    'username': username,
                    'verified': verified,
                }

                if not verified:
                    params['login'] = 'le credenziali non sono corrette'

                check = Utente.get_from_associated(str(username))

                if check:
                    params['verified'] = False
                    params['login'] = 'le credenziali immesse sono gia associate ad un account'

                self.response.headers['Content-Type'] = 'text/html'
                self.response.write(template.render(params))

            except HTTPException:
                webapp2.abort(code=503)

        if self.request.get('conferma'):
            user = self.request.get('new_user')
            username = self.request.get('username')
            nome = self.request.get('nome')
            cognome = self.request.get('cognome')
            email = self.request.get('email')

            params = {
                # Nome di MyAnimeList
                'username': username,
                'verified': True,
            }

            valid = validate_email(email)

            if user == '':
                params['user_err'] = 'inserisci un username'
            else:
                params['user'] = user

            if nome == '':
                params['nome_err'] = 'inserisci il tuo nome'
            else:
                params['nome'] = nome

            if cognome == '':
                params['cognome_err'] = 'inserisci il tuo cognome'
            else:
                params['cognome'] = cognome

            if email == '':
                params['email_err'] = 'inserisci un indirizzo email'
            elif not valid:
                params['email_err'] = 'l\'indirizzo email inserito non e valido'
            else:
                params['email'] = email

            # Controllo se qualche flag di errore e settato
            err_check = False
            for k in params.keys():
                if 'err' in k:
                    err_check = True
                    break

            # Non ci sono errori immessi dall utente
            if not err_check:
                ret = Utente.get_or_insert(
                    username=user,
                    email=email,
                    nome=nome,
                    cognome=cognome,
                    tipo='mal_user',
                    associated_user=str(username)
                )

                print ret

                # Controllo se ci sono errori di unicita sui parametri inseriti
                if ret == 0:
                    current_page = self.session['current_page']
                    return self.redirect(current_page)

                elif ret == 1:
                    params['user_err'] = 'l\' username inserito esiste gia'
                    params['user'] = ''

                elif ret == 3:
                    params['email_err'] = 'l\' email non e disponibile'
                    params['email'] = ''

                t = JENV.get_template('signup_mal.html')
                self.response.headers['Content-Type'] = 'text/html'
                self.response.write(t.render(params))

            # Ci sono errori
            else:
                t = JENV.get_template('signup_mal.html')
                self.response.headers['Content-Type'] = 'text/html'
                self.response.write(t.render(params))


class LoginMalHandler(BaseHandler):
    def get(self, template = JENV.get_template('login_mal.html')):
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(template.render())

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        try:
            user = Utente.get_from_associated(associated=str(username))
            if check_mal_account(username=username, passw=password) and user:

                self.session['type'] = 'mal_user'
                self.session['user_name'] = user.key.id()
                self.session['name'] = user.nome
                self.session['last_name'] = user.cognome
                self.session['mal_name'] = username
                self.session['mal_pass'] = password

                current_page = self.session['current_page']

                self.redirect(current_page)
            else:
                errors = {
                    'login': 'le credenziali non sono corrette'
                }
                t = JENV.get_template('login_mal.html')
                self.response.headers['Content-Type'] = 'text/html'
                self.response.write(t.render(errors))
        except HTTPException:
            webapp2.abort(code=503)


class LoginHandler(BaseHandler):
    def get(self, template = JENV.get_template('login.html')):
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write(template.render())

    def post(self):
        user_name = self.request.get('username')
        password = self.request.get('password')

        errors = {}

        if password == '':
            errors['password_err'] = 'inserisci una password'

        # Controllo correttezza username
        if user_name == '':
            errors['username_err'] = 'inserisci un username'
        elif not Utente.check_user(user_name):
            errors['username_err'] = 'l\'username inserito non esiste'
        else:
            # Username corretto, controllo correttezza password
            errors['username'] = user_name
            user = Utente.normal_login(
                username=user_name,
                passw=password
            )
            if user:
                self.session['type'] = 'normal_user'
                self.session['user_name'] = user.key.id()
                self.session['name'] = user.nome
                self.session['last_name'] = user.cognome
            else:
                errors['password_err'] = 'la password inserita e errata'

        # Controlla se qualche flag errore e stato impostato
        err_check = False
        for k in errors.keys():
            if 'err' in k:
                err_check = True
                break

        if not err_check:
            current_page = self.session['current_page']
            self.redirect(current_page)
        else:
            t = JENV.get_template('login.html')
            self.response.headers['Content-Type'] = 'text/html'
            self.response.write(t.render(errors))


class LogoutHandler(BaseHandler):
    def get(self):

        self.session['user_name'] = None
        self.session['last_name'] = None
        self.session['name'] = None
        if self.session['type'] == 'mal_user':
            self.session['mal_name'] = None
            self.session['mal_pass'] = None
        self.session['type'] = None

        current_page = self.session['current_page']

        self.redirect(current_page)
