import base64
import webapp2
import datetime
from utils.api_mal import check_mal_account
from models.list import Watching
from models.anime import Anime
from models.user import Utente
from handlers.base import BaseHandler


class AddAPI(BaseHandler):
    def post(self):

        auth  = self.request.authorization
        anime = self.request.get('id_anime')

        # controllo se la sessione e settata
        if 'token' in self.session:
            # controllo se il token e valido
            if datetime.datetime.utcnow() > self.session['token']['expire']:
                webapp2.abort(code=401, detail='token scaduto')
        else:
            webapp2.abort(code=401, detail='effettuare l\'autenticazione')

        a = Anime.get_by_id(anime)

        # L'anime immesso non e corretto
        if not a:
            webapp2.abort(code=400, detail='anime non esistente')

        # controllo se l'header authorization e settato
        if not auth:
            webapp2.abort(code=401, detail='inserire un access token')

        try:
            auth = base64.b64decode(auth[1])
        except TypeError:
            webapp2.abort(code=400, detail='impossibile decodificare il token')

        # Controllo se l'header authorization immesso
        # corrisponde a qualcosa di sensato
        if ':' not in auth or auth[-1] == ':':
            webapp2.abort(code=401, detail='il token non ha un formato valido')

        user  = auth.split(':')[0]
        passw = auth.split(':')[1]

        mal_user = False

        # Controllo se l'utente e realmente esistente
        if Utente.check_user(user) or \
                Utente.get_from_associated(user):

            # per capire di che tipo di account si tratta
            nr = Utente.normal_login(user, passw)
            if not nr:
                if check_mal_account(user, passw):
                    mal_user = True

            # Controllo sulla password
            if nr or mal_user:
                if mal_user:
                    user = Utente.get_from_associated(user)
                    user = user.key.id()

                return Watching.insert(user, anime)

        webapp2.abort(code=401, detail='le credenziali sono errate')
