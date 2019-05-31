import base64
import webapp2
import datetime
from lxml import etree
from handlers.base import BaseHandler
from models.user import Utente
from utils.api_mal import check_mal_account


class LoginAPI(BaseHandler):
    def post(self):

        auth  = self.request.get('auth')

        # controllo se la stringa passata ha un formato corretto
        if ':' not in auth or auth[-1] == ':':
            webapp2.abort(code=400, detail='le credenziali non hanno un formato corretto')

        user  = auth.split(':')[0]
        passw = auth.split(':')[1]

        user = str(user)

        self.response.headers['Content-Type'] = 'application/xml'

        # Controllo se l'utente e realmente esistente
        if Utente.check_user(user) or \
                Utente.get_from_associated(user):
            # Controllo sulla password
            if Utente.normal_login(user, passw) or \
                    check_mal_account(user, passw):

                token = base64.b64encode(auth)

                exp_time = datetime.datetime.utcnow() + \
                           datetime.timedelta(seconds=1200)

                token_dict = {
                    "token": token,
                    "expire": exp_time
                }

                self.session['token'] = token_dict

                root = etree.Element('user')
                u = etree.SubElement(root, 'username')
                t = etree.SubElement(root, 'token')
                e = etree.SubElement(root, 'expire')

                u.text = user
                t.text = token
                e.text = str(exp_time)

                return self.response.write(
                    etree.tostring(root, pretty_print=True)
                )
        webapp2.abort(code=401, detail='le credenziali sono errate')

    def get(self):
        self.post()
